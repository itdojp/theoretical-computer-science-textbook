source "https://rubygems.org"

# GitHub Pages公式gem
gem "github-pages", "~> 232", group: :jekyll_plugins

# jekyll-github-metadata -> OctokitのFaraday 2 retry middleware
gem "faraday-retry", "~> 2.4"

# Windows対応
gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]

# タイムゾーン情報
gem "tzinfo-data", platforms: [:mingw, :mswin, :x64_mingw, :jruby]

# GitHub Pages標準プラグイン
group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.12"
  gem "jekyll-sitemap"
  gem "jekyll-seo-tag"
end

# 開発用gem
group :development do
  gem "jekyll", "~> 3.10.0"
  gem "minima", "~> 2.5"
end
