import sys
import time
import argparse
import csv
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed

class PageScanner:
    def __init__(self, start_url=None, max_depth=2, delay=1.0, exclude_patterns=None, workers=4):
        self.start_url = start_url
        self.max_depth = max_depth
        self.delay = delay
        self.exclude_patterns = exclude_patterns or []
        self.workers = workers
        self.visited = set()

    def crawl(self, limit=None):
        queue = [(self.start_url, 0)]
        urls_to_scan = []

        while queue:
            url, depth = queue.pop(0)
            if url in self.visited or depth > self.max_depth:
                continue

            print(f"[+] Queued for scan ({depth}): {url}")
            self.visited.add(url)
            urls_to_scan.append(url)

            if limit is not None and len(urls_to_scan) >= limit:
                break

            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, wait_until="networkidle")
                    html = page.content()
                    browser.close()
            except Exception:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup.find_all('a', href=True):
                link = urljoin(url, tag['href'])
                should_exclude = any(pattern in link for pattern in self.exclude_patterns)
                if self.is_internal(url, link) and link not in self.visited and not should_exclude:
                    queue.append((link, depth + 1))

        return urls_to_scan

    def scan_url(self, url):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto(url, wait_until="networkidle")
                html = page.content()
                cookies = context.cookies()
                set_cookie_headers = page.evaluate("() => document.cookie")
                browser.close()
        except Exception as e:
            print(f"[!] Error visiting {url}: {e}")
            return None

        soup = BeautifulSoup(html, 'html.parser')
        return self.parse(url, soup, cookies, set_cookie_headers)

    def is_internal(self, base_url, test_url):
        base_domain = urlparse(base_url).netloc
        test_domain = urlparse(test_url).netloc
        return base_domain == test_domain

    def parse(self, page_url, soup, cookies, set_cookie_headers):
        scripts = [tag.get('src') for tag in soup.find_all('script') if tag.get('src')]
        iframes = [tag.get('src') for tag in soup.find_all('iframe') if tag.get('src')]
        links = [tag.get('href') for tag in soup.find_all('link') if tag.get('href')]
        all_sources = scripts + iframes + links

        findings = {
            'url': page_url,
            'facebook_plugins': [],
            'twitter_plugins': [],
            'linkedin_plugins': [],
            'instagram_plugins': [],
            'youtube_embeds': [],
            'tiktok_embeds': [],
            'analytics': [],
            'cookie_trackers': [],
            'suspicious_domains': [],
            'cookies': []
        }

        patterns = {
            'facebook_plugins': ['facebook.com/plugins', 'connect.facebook.net'],
            'twitter_plugins': ['platform.twitter.com', 'twitter.com/widgets.js'],
            'linkedin_plugins': ['platform.linkedin.com'],
            'instagram_plugins': ['instagram.com/embed', 'instagr.am'],
            'youtube_embeds': ['youtube.com/embed', 'youtu.be'],
            'tiktok_embeds': ['tiktok.com/embed'],
            'analytics': [
                'googletagmanager.com/gtag/js', 'google-analytics.com', 'gtag/js', 'analytics.js',
                'plausible.io/js', 'matomo.js', 'hotjar.com', 'mixpanel.com', 'segment.com',
                'amplitude.com'
            ],
            'cookie_trackers': [
                'connect.facebook.net/en_US/fbevents.js', 'facebook.com/tr',
                'googleads.g.doubleclick.net/pagead', 'googletagmanager.com/gtag/js',
                'bat.bing.com/bat.js', 'snap.licdn.com/li.lms-analytics/insight.min.js',
                't.co/i/adsct', 'ads-twitter.com/uwt.js', 'cdn.taboola.com/libtrc/unip/',
                'analytics.tiktok.com/i18n/pixel'
            ]
        }

        cookie_name_patterns = [
            '_fbp', '_fbc', 'fr', 'ajs_user_id', 'ajs_anonymous_id', 'amplitude_id_',
            'optimizelyEndUserId', 'hubspotutk', 'intercom-id-', 'intercom-session-', 'pardot',
            'driftt_aid', 'tracking_id', 'visitor_id', '_ga', '_gid', '_gat', '__hstc', '__hssrc',
            '__cf_bm', '__cfruid', 'MXP_TRACKINGID'
        ]

        for src in all_sources:
            for key, subs in patterns.items():
                if any(sub in src for sub in subs):
                    findings[key].append(src)

        domain = urlparse(page_url).netloc
        findings['suspicious_domains'] = [
            src for src in all_sources
            if (
                src and
                urlparse(src).netloc and
                domain not in src and
                not any(src in v for k, v in findings.items() if k != 'suspicious_domains')
            )
        ]

        cookie_matches = []
        for c in cookies:
            for pattern in cookie_name_patterns:
                if pattern in c['name']:
                    cookie_matches.append(c['name'])

        if set_cookie_headers:
            for pattern in cookie_name_patterns:
                if pattern in set_cookie_headers:
                    cookie_matches.append(f"header:{pattern}")

        findings['cookies'] = list(set(cookie_matches))
        return findings


def export_to_csv(results, filename="scan_results.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Detected', 'Source', 'Cookies'])
        for item in results:
            detected = any(len(v) > 0 for k, v in item.items() if k not in ['url', 'cookies'])
            flat_sources = []
            for k, v in item.items():
                if k not in ['url', 'cookies'] and v:
                    flat_sources.extend(v)
            writer.writerow([item['url'], 'Yes' if detected else 'No', '; '.join(flat_sources), '; '.join(item['cookies'])])


def main():
    parser = argparse.ArgumentParser(description="Scans website for embedded social media elements")
    parser.add_argument("-u", "--url", help="Starting url to scan", required=True)
    parser.add_argument("-d", type=int, help="defines how deep we want scan to go", default=2)
    parser.add_argument("-e", "--exclude", nargs='*', default=[], help="List of substrings to exclude from crawling (e.g., logout, contact)")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Number of parallel workers to fetch URLs")
    parser.add_argument("-o", "--output", help="Output CSV file", default="scan_results.csv")
    parser.add_argument("-s", "--scan-limit", type=int, help="Maximum number of pages to scan")
    args = parser.parse_args()

    scanner = PageScanner(start_url=args.url, max_depth=args.d, delay=1.5, exclude_patterns=args.exclude, workers=args.workers)

    results = []

    try:
        try:
            urls = scanner.crawl(limit=args.scan_limit)
        except KeyboardInterrupt:
            print("\n[!] Crawl interrupted. Scanning what was collected so far...")
            urls = list(scanner.visited)

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_url = {executor.submit(scanner.scan_url, url): url for url in urls}
            for future in as_completed(future_to_url):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"[!] Error scanning URL: {e}")

    except KeyboardInterrupt:
        print("\n[!] Scan interrupted. Saving partial results...")

    export_to_csv(results, args.output)
    print(f"[+] Results saved to: {args.output}")


if __name__ == "__main__":
    main()
