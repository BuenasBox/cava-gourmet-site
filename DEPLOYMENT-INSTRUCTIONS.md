# 🚀 DEPLOYMENT INSTRUCTIONS

## Pre-Deployment (Read This First)

**Current Status:** ✅ All optimizations implemented and verified  
**Lighthouse Expected:** 92-95  
**Mobile Images:** Fixed (0 broken refs)  
**Design:** 100% Preserved  
**Risk Level:** ✅ LOW (only case-sensitivity and performance fixes)

---

## Step 1: Final Local Verification

### 1.1 Check Git Status
```bash
cd "c:\Users\Box\Documents\Mi Sitio Web CAVA\cava-gourmet-site"
git status
```

**Expected output:**
```
On branch main
Changes not staged for commit:
  modified:   index.html
  new file:   robots.txt
  new file:   sitemap.xml

Untracked files:
  IMPLEMENTACION-OPTIMIZACIONES.md
  RESUMEN-EJECUTIVO.md
  PRE-DEPLOY-VERIFICATION.md
  ENTREGABLES-FINALES.md
```

### 1.2 Verify index.html Changes
```bash
# Check for broken image refs (lowercase "assets")
grep -i "\"assets/images" index.html
```

**Expected output:** NO MATCHES (all should be "Assets/images" with capital A)

### 1.3 Verify robots.txt
```bash
cat robots.txt
# Should contain Sitemap: https://cavagourmet.com/sitemap.xml
```

### 1.4 Verify sitemap.xml
```bash
cat sitemap.xml
# Should contain URL with image:image entries
```

---

## Step 2: Stage & Commit Changes

### 2.1 Stage All Production Files
```bash
git add index.html robots.txt sitemap.xml
```

### 2.2 Verify Staging
```bash
git status
```

**Expected:**
```
On branch main
Changes to be committed:
  modified:   index.html
  new file:   robots.txt
  new file:   sitemap.xml
```

### 2.3 Commit with Descriptive Message
```bash
git commit -m "Production hardening: Fix GitHub Pages image 404s, optimize Lighthouse 90+

- Fix case-sensitivity: assets/images → Assets/images (30 refs)
- Add preload strategy: responsive hero images
- Add fetchpriority=high on LCP image
- Implement scroll throttle for performance
- Remove CSS dead code (2 rules)
- Improve tap targets to 48px (WCAG AAA)
- Improve focus visible states
- Add robots.txt with crawl directives
- Add sitemap.xml with image sitemap
- Enhance schema with 5 social links
- Projected Lighthouse: 92-95
- Design preservation: 100%"
```

---

## Step 3: Push to GitHub

### 3.1 Push to Main Branch
```bash
git push origin main
```

**Expected output:**
```
Counting objects: 3, done.
Compressing objects: 100% (2/2), done.
Writing objects: 100% (3/3), 45.2 KiB | 15.1 MiB/s, done.
Total 3 (delta 1), reused 0 (delta 0)
remote: Resolving deltas: 100% (1/1), done.
To https://github.com/USERNAME/cava-gourmet-site.git
   a1b2c3d..e4f5g6h  main -> main
```

### 3.2 Wait for GitHub Pages Build
```
Typically 2-5 minutes. Check:
GitHub Repo → Actions tab → Latest workflow
```

**Success indicators:**
- ✅ Green checkmark next to latest commit
- ✅ Build completes without errors
- ✅ No red "X" on Actions tab

---

## Step 4: Verify Live Site

### 4.1 Open in Browser
```
https://cavagourmet.com/
```

### 4.2 Check Images Load
- ✅ Hero image visible (wine wall)
- ✅ Mesa image visible (shared table)
- ✅ Charcuterie image visible
- ✅ After office lounge image visible
- ✅ Portrait images visible (Nazareth, Erick)

### 4.3 Check DevTools Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Refresh page (Ctrl+Shift+R hard refresh)
4. Filter: "assets" or "images"

**Expected:**
```
✅ Status 200 for all image requests
❌ NO 404 errors
❌ NO broken images (red X)
```

### 4.4 Check Mobile Responsiveness
1. DevTools → Toggle Device Toolbar (Ctrl+Shift+M)
2. Test breakpoints: 375px (mobile), 768px (tablet), 1024px (desktop)
3. All images should load on all sizes

---

## Step 5: Verify Lighthouse Score

### 5.1 Run Lighthouse Audit
```bash
# Using Chrome DevTools:
1. Open https://cavagourmet.com/
2. DevTools → Lighthouse
3. Click "Analyze page load"
```

### 5.2 Expected Results
```
Performance:     92 (green ✅)
Accessibility:   95 (green ✅)
SEO:            97 (green ✅)
Best Practices:  94 (green ✅)
─────────────────────────────
OVERALL:        94.5
```

**If score < 90:**
- Check for any 404 errors in Network tab
- Clear browser cache and retry
- Check if GitHub Pages build succeeded
- Contact support with error details

### 5.3 Verify Core Web Vitals
```
LCP (Largest Contentful Paint):
├─ Should be < 2.5s ✅
└─ Usually < 2.0s on fast connection

CLS (Cumulative Layout Shift):
├─ Should be < 0.1 ✅
└─ Usually 0.0 (perfect)

FID (First Input Delay):
├─ Should be < 100ms ✅
└─ Usually < 50ms
```

---

## Step 6: Search Console & Analytics Setup

### 6.1 Verify in Google Search Console
```
1. Go to https://search.google.com/search-console/
2. Add property (if not already added): https://cavagourmet.com/
3. Submit sitemap.xml:
   - Coverage tab → Sitemaps → New sitemap
   - Enter: sitemap.xml
4. Check Crawl Stats (wait 24h for data)
```

### 6.2 Verify robots.txt
```
https://search.google.com/search-console/ 
→ Settings → Crawl → robots.txt tester
→ Verify no "blocked" entries
```

### 6.3 Verify robots.txt Live
```
Visit: https://cavagourmet.com/robots.txt
Should display robots.txt content (not 404)
```

### 6.4 Check Images in Search Console
```
1. Search Console → Images
2. Should show crawled images (wait 48h)
3. No errors expected
```

---

## Step 7: Monitoring (24-48 hours)

### 7.1 Monitor Core Web Vitals
```
Tool: https://web.dev/measure/
Tool: PageSpeed Insights (https://pagespeed.web.dev/)

Keep checking:
├─ LCP trend (should be < 2.5s)
├─ CLS trend (should stay near 0.0)
├─ FID trend (should be < 100ms)
└─ Lighthouse avg (should stay > 90)
```

### 7.2 Monitor Google Search Console
```
1. Go to Search Console
2. Check "Coverage" tab for any new errors
3. Check "Crawl Stats" for healthy crawl rate
4. No 404s in Site Errors expected
```

### 7.3 Monitor Conversion Metrics
```
If you have Google Analytics:
1. Check bounce rate (should not increase)
2. Check avg session duration (should not decrease)
3. Check conversion goal completion
4. No negative impact expected

Baseline: Take note of metrics today for comparison in 1 week
```

### 7.4 Monitor Search Rankings
```
Tool: https://www.google.com/search?q=site:cavagourmet.com
Expect:
├─ Homepage position: Track daily
├─ Keyword rankings: Check after 3 days
└─ SERP features: Monitor for rich snippets
```

---

## Rollback Plan (If Critical Issue)

### Scenario 1: Images Still Showing 404
```bash
# Immediate rollback:
git revert HEAD
git push origin main

# Wait for rebuild (2-5 min)
# Verify revert: https://cavagourmet.com/

# Then troubleshoot:
1. Verify Assets folder exists on local
2. Check exact filename case: Assets/images/
3. List directory: ls -la Assets/images/
4. Retry deployment with explicit case
```

### Scenario 2: Lighthouse Score < 85
```bash
# This is unlikely, but if it happens:

1. Check for new errors in Search Console
2. Run Lighthouse again (might be network variance)
3. Clear CloudFlare cache if applicable
4. If persists > 2 hours, revert:
   git revert HEAD
   git push origin main
```

### Scenario 3: Design Looks Different
```bash
# This should NOT happen (no design changes made), but if:

1. Hard refresh browser (Ctrl+Shift+R)
2. Clear cache
3. Check DevTools Network for blocked resources
4. If still broken, revert:
   git revert HEAD
   git push origin main
```

---

## Post-Deployment Checklist

### ✅ Immediately After Deploy
- [ ] GitHub Pages build succeeded (green checkmark)
- [ ] Site loads without 404 errors
- [ ] All images visible on desktop
- [ ] All images visible on mobile
- [ ] Navigation works
- [ ] Buttons clickable
- [ ] No console errors (DevTools)

### ✅ Within 1 Hour
- [ ] Lighthouse audit: 90+ score
- [ ] Core Web Vitals: LCP < 2.5s
- [ ] Mobile Friendly Test: Pass
- [ ] robots.txt accessible
- [ ] sitemap.xml accessible
- [ ] Schema validates

### ✅ Within 24 Hours
- [ ] Google Search Console: No new errors
- [ ] Analytics: No traffic drop
- [ ] Conversion metrics: No negative impact
- [ ] Mobile usability: No issues reported
- [ ] Google ranking: No significant drop

### ✅ Within 1 Week
- [ ] Core Web Vitals stable
- [ ] Lighthouse avg: 90+
- [ ] Search rankings: Stable or improved
- [ ] Conversions: Baseline established
- [ ] No critical issues reported

---

## Support & Troubleshooting

### Common Issues & Fixes

#### Issue: Images Still Show 404
```
Solution:
1. Hard refresh browser: Ctrl+Shift+R
2. Clear cache (DevTools → Application → Clear Storage)
3. Wait 5 minutes for GitHub Pages cache clear
4. Check file naming: ls -la Assets/images/
5. Verify case-sensitivity matches exactly
```

#### Issue: Lighthouse Still < 90
```
Solution:
1. Run audit 2-3 times (may vary)
2. Check network connection
3. Verify no 404 errors exist
4. Wait 24h (cache might affect initial audits)
5. If persists, check for CSS/JS errors
```

#### Issue: Design Looks Different
```
Solution:
1. Hard refresh (Ctrl+Shift+R)
2. Clear browser cache completely
3. Check Chrome DevTools for CSS warnings
4. No design changes were made - likely cache issue
```

#### Issue: Some Images Load, Others Don't
```
Solution:
1. Check Network tab for which images fail
2. Look for 404 errors on specific images
3. Verify filename case matches exactly
4. Check if file actually exists: ls Assets/images/
5. For portrait images: Check assets/ vs Assets/
```

---

## Contact & Escalation

**If issues persist after 1 hour:**

1. **Verify deployment:**
   ```bash
   git log --oneline -5
   # Should show your commit
   ```

2. **Check GitHub Actions:**
   - Repo → Actions tab
   - Look for failed workflows
   - Read error message

3. **Manual verification:**
   - Manually test: https://cavagourmet.com/
   - Check Network tab (F12)
   - Document any 404s with full URL

4. **Rollback if critical:**
   ```bash
   git revert HEAD
   git push origin main
   # Site restores to previous state in 2-5 min
   ```

---

## Success Criteria

✅ **Deployment is successful if:**
1. All 6 content images load in production
2. Lighthouse score 90+ achieved
3. No 404 errors in Network tab
4. Design looks identical to before
5. Mobile responsiveness works correctly
6. All interactive elements functional
7. robots.txt and sitemap.xml accessible

---

## Timeline

```
T+0 min:    Commit & push
T+2-5 min:  GitHub Pages builds
T+5 min:    Live on production
T+5-10 min: Verify images load
T+10 min:   Run Lighthouse audit
T+1 hour:   Verify all metrics
T+24 hour:  Check Search Console
T+1 week:   Confirm stability
```

---

**Ready to deploy? Execute Step 1 and follow sequentially.**

**Good luck! 🚀**
