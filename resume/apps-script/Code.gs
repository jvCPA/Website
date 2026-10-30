/**
 * Resume landing page: Google Apps Script web app.
 *
 * Setup (full steps in README.md):
 *   1. Paste your Google Sheet ID into SHEET_ID.
 *   2. Put the address that should receive contact messages into MY_EMAIL.
 *   3. Deploy > New deployment > Web app (Execute as: Me, Who has access: Anyone).
 */

// ── Settings ────────────────────────────────────────────────────────────────
var SHEET_ID = 'PASTE_YOUR_GOOGLE_SHEET_ID_HERE'; // TEMP - replace
var MY_EMAIL = 'hello@example.com';               // TEMP - replace
var SHEET_NAME = 'Contact form';
var PAGE_TITLE = 'Jorge Vincent Coral · Accountant & AI Automation';
// ────────────────────────────────────────────────────────────────────────────

function doGet() {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle(PAGE_TITLE)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, viewport-fit=cover')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL); // lets Google Sites embed it
}

/** Inlines another project file (Styles, Scene, App, Config) into Index.html. */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/**
 * Called from the page with google.script.run.submitContact({name, email, message, website}).
 * `website` is a hidden honeypot field: people never fill it, bots usually do.
 */
function submitContact(form) {
  form = form || {};
  var name = clean_(form.name, 120);
  var email = clean_(form.email, 200);
  var message = clean_(form.message, 5000);

  if (form.website) {
    return { ok: true }; // honeypot filled: quietly accept and drop it
  }
  if (!name || !message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error('Please fill in your name, a valid email and a message.');
  }

  // Simple flood guard: at most 5 messages per sender email per hour.
  var cache = CacheService.getScriptCache();
  var key = 'contact_' + Utilities.base64EncodeWebSafe(email.toLowerCase()).slice(0, 200);
  var count = Number(cache.get(key) || 0);
  if (count >= 5) {
    throw new Error('Too many messages in a short time. Please try again later.');
  }
  cache.put(key, String(count + 1), 3600);

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var ss = SpreadsheetApp.openById(SHEET_ID);
    var sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['Received', 'Name', 'Email', 'Message']);
      sheet.setFrozenRows(1);
    }
    // a leading apostrophe stops a message starting with "=" from running as a formula
    sheet.appendRow([new Date(), safeCell_(name), safeCell_(email), safeCell_(message)]);
  } finally {
    lock.releaseLock();
  }

  MailApp.sendEmail({
    to: MY_EMAIL,
    replyTo: email,
    subject: 'Website message from ' + name,
    body: 'Name: ' + name + '\nEmail: ' + email + '\n\n' + message
  });

  return { ok: true };
}

function clean_(value, max) {
  return String(value || '').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, max);
}

function safeCell_(value) {
  return /^[=+\-@]/.test(value) ? "'" + value : value;
}

/**
 * Run this once from the editor (select "testSetup" > Run) after filling in SHEET_ID and MY_EMAIL.
 * It asks for permission, checks the sheet opens and sends you a test email.
 */
function testSetup() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  MailApp.sendEmail(MY_EMAIL, 'Resume site: setup test', 'Your contact form is connected to "' + ss.getName() + '".');
  Logger.log('OK: sheet "%s" found, test email sent to %s', ss.getName(), MY_EMAIL);
}
