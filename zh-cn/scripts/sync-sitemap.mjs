import fs from "node:fs/promises";
import path from "node:path";

const UPSTREAM_SITEMAP_URL = "https://docs.openwebui.com/sitemap.xml";
const BUILD_SITEMAP_PATH = path.join("build", "sitemap.xml");

function targetOrigin(domain) {
	const value = domain.trim();
	const url = new URL(/^https?:\/\//i.test(value) ? value : `https://${value}`);

	if (url.protocol !== "http:" && url.protocol !== "https:") {
		throw new Error("DOMAIN must use an HTTP or HTTPS URL.");
	}

	return url.origin;
}

const domain = process.env.DOMAIN;

if (!domain) {
	console.log("DOMAIN is not set; skipped upstream sitemap synchronization.");
	process.exit(0);
}

const response = await fetch(UPSTREAM_SITEMAP_URL, {
	headers: { Accept: "application/xml,text/xml;q=0.9,*/*;q=0.8" },
});

if (!response.ok) {
	throw new Error(
		`Failed to download upstream sitemap (HTTP ${response.status}).`
	);
}

const sitemap = await response.text();
if (!sitemap.includes("<urlset")) {
	throw new Error("Upstream sitemap does not contain a urlset document.");
}

const origin = targetOrigin(domain);
const rewrittenSitemap = sitemap.replaceAll(
	"https://docs.openwebui.com",
	origin
);

await fs.writeFile(BUILD_SITEMAP_PATH, rewrittenSitemap, "utf8");
console.log("Synchronized upstream sitemap.xml for the configured DOMAIN.");
