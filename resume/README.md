# Resume landing page (Google Apps Script + Google Sites)

A one-page resume for Jorge Vincent Coral with a 3D hero: a 360° photo turntable on a glowing
plinth, with eight featured certificates orbiting around it. It runs as a Google Apps Script web
app, so it can be embedded in Google Sites, and the contact form saves messages to a Google Sheet
and emails you.

## What is in this folder

| Path | What it is |
|---|---|
| `apps-script/` | The files you copy into Apps Script: `Code.gs`, `Index.html`, `Styles.html`, `Scene.html`, `App.html`, `Config.html`, `appsscript.json` |
| `apps-script/Config.html` | **All your personal details** (name, text, skills, jobs, certificates). Search for `TEMP - replace` |
| `assets/turntable/` | `turntable.png` (your original sheet), `atlas.webp` (all 19 cleaned frames), `front.webp`, `frames.json` (angles) |
| `assets/certs/` | Cleaned certificate images (`<id>.webp`) and thumbnails (`<id>-thumb.webp`) |
| `assets/certs/originals/` | Your original uploads. The page never uses these |
| `preview/index.html` | The same page running without Apps Script, for testing |
| `tools/` | Scripts that rebuild the images and the preview |
| `screenshots/` | Screenshots of the finished page |

---

## 1. Put in your real details

Open `apps-script/Config.html` and replace every line marked `// TEMP - replace`:
tagline, location, email, LinkedIn link, stats, about text, skills, jobs and education.
Text in square brackets such as `[Company Name]` is a placeholder too.

In `apps-script/Code.gs`, two settings at the top also need changing (step 3).

## 2. Create the Google Sheet

1. Go to [sheets.new](https://sheets.new) and name the sheet, for example "Website messages".
2. Copy its ID from the address bar: the long code between `/d/` and `/edit`.
   `https://docs.google.com/spreadsheets/d/`**`1AbC...xyz`**`/edit`
3. You don't need to add headings: the first message creates a "Contact form" tab with
   Received / Name / Email / Message columns.

## 3. Create the Apps Script project

1. Go to [script.google.com](https://script.google.com) and click **New project**. Name it "Resume site".
2. **Code.gs:** delete what is there and paste in the contents of `apps-script/Code.gs`.
   At the top, set:
   - `SHEET_ID` to the ID from step 2
   - `MY_EMAIL` to the address that should receive messages
3. **HTML files:** click **+** next to *Files*, then **HTML**, and create five files named exactly
   `Index`, `Styles`, `Scene`, `App` and `Config` (Apps Script adds `.html` itself).
   Paste the matching file from `apps-script/` into each one.
4. **appsscript.json:** open *Project Settings* (gear icon), tick **Show "appsscript.json" manifest
   file in editor**, go back to the editor, open `appsscript.json` and replace it with ours.
5. Click **Save**.
6. Choose `testSetup` in the function menu at the top and click **Run**. Google asks for
   permission (sheets and sending email as you); click through *Advanced → Go to Resume site*.
   You should get a "setup test" email within a minute.

## 4. Deploy it as a web app

1. Click **Deploy → New deployment**.
2. Click the gear next to *Select type* and choose **Web app**.
3. Set **Execute as: Me** and **Who has access: Anyone**.
4. Click **Deploy** and copy the **Web app URL** (it ends in `/exec`). Open it to check the page.

**After any later change:** **Deploy → Manage deployments**, click the pencil, set
*Version* to **New version**, then **Deploy**. The URL stays the same.

## 5. Embed it in Google Sites

1. In your Google Site, click **Insert → Embed**.
2. Choose **By URL**, paste the `/exec` URL and pick **Whole page**. Click **Insert**.
3. Drag the embed to the full width of the page and make it tall (the page scrolls inside the box,
   so around one screen tall works well).
4. Click **Publish**.

`Code.gs` already allows embedding (`setXFrameOptionsMode(ALLOWALL)`). Links such as LinkedIn and
"Verify credential" open outside the embed.

---

## Updating images

The page loads images from this GitHub repository through jsDelivr, using a link pinned to one
exact commit, for example:

```
https://cdn.jsdelivr.net/gh/jvCPA/Website@<commit>/resume/assets/
```

Pinned links never change, so visitors never see a half-updated set of images. The price is that
after changing images you have to point the page at the new commit:

1. Add or replace files in `resume/assets/` (for certificates, run the tool below), then commit and
   push to GitHub.
2. Copy the new commit's ID: on GitHub, open *Commits* and click the copy icon next to the latest one
   (or run `git rev-parse HEAD`).
3. In `apps-script/Config.html`, replace the long code after `@` in `ASSET_BASE` with the new ID.
4. Paste the updated `Config` into Apps Script and deploy a new version (step 4).

### Adding or changing a certificate

1. Put the original file in `assets/certs/originals/`.
2. Add a line for it to the `CERTS` list in `tools/process_certs.py` (and blur boxes for any ID
   numbers or QR codes), then run from the repo root:

   ```bash
   pip install pymupdf pillow opencv-python-headless numpy
   ```

   ```bash
   python3 resume/tools/process_certs.py
   ```

3. Add a matching entry to `certificates` in `Config.html` (`id` = the name used in the script).
4. Follow "Updating images" above.

To change which eight orbit the figure, move `featured: true` between certificates (keep it to eight).

### Using a real 3D model instead of the photo turntable

Put a GLB file at `resume/assets/avatar.glb`, push, and update the commit ID as above. The page
checks for it on load and uses it in place of the photos.

### Rebuilding the turntable

```bash
pip install "rembg[cpu]" pillow numpy
```

```bash
python3 resume/tools/process_turntable.py
```

The viewing angle of each frame is set in `ANGLES` inside that script.

---

## Testing without Apps Script

`preview/index.html` is the same page with images loaded from the repo folder and a pretend
`google.script.run`. It must be served over http (browsers block 3D scripts opened from a file):

```bash
python3 -m http.server 8000
```

Run that from the repo root, then open <http://localhost:8000/resume/preview/>. In the preview,
the contact form always "sends"; a message containing the word **fail** shows the error state.

After editing anything in `apps-script/`, rebuild the preview:

```bash
node resume/tools/build_preview.mjs
```

## How the page behaves

- **3D hero:** the figure turns slowly and pauses on the front view each turn; drag or swipe to turn
  it (with inertia). Hover a certificate to stop it and make it glow; click to bring it to the front
  with its details. Keyboard users can Tab into the hero to get a list of the eight certificates.
- **Still hero:** with "reduce motion" switched on, without WebGL, or if the 3D code cannot load,
  the hero shows the front photo and a grid of the featured certificates instead.
- **Performance:** rendering stops when the hero is scrolled away or the tab is hidden. Phones get
  fewer particles, no bloom and no background props.

## Troubleshooting

- **The still hero shows instead of 3D:** check reduce-motion settings and that `cdn.jsdelivr.net`
  is not blocked. The browser console says why (`[resume] still hero: ...`).
- **Images missing:** the commit ID in `ASSET_BASE` must be a commit that has been pushed to GitHub,
  and the repository must stay public.
- **Form says it failed:** run `testSetup` again from the editor and read the error; usually the
  `SHEET_ID` is wrong or permission was not granted. Daily email limits for MailApp also apply.
- **Page not updating:** deploy a **new version** (step 4); saving alone does not publish.
