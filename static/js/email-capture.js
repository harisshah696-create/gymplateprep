// ─── EmailJS Configuration ───────────────────────────────────────
// To set this up:
//   1. Sign up at https://www.emailjs.com/ (free tier: 200 emails/month)
//   2. Go to Email Services → Add a new email service (Gmail, Outlook, or SMTP)
//   3. Go to Email Templates → Create New Template
//      - Template content: paste the meal plan, shopping list, and calorie
//        calculator info. Use {{email}} as the recipient variable.
//   4. Get your Public Key (Account → API Keys), Service ID, and Template ID
//   5. Fill in the three values below:

var EMAILJS_PUBLIC_KEY  = "YOUR_PUBLIC_KEY";   // e.g. "abc123def456"
var EMAILJS_SERVICE_ID  = "YOUR_SERVICE_ID";   // e.g. "service_abc123"
var EMAILJS_TEMPLATE_ID = "YOUR_TEMPLATE_ID";  // e.g. "template_xyz789"

// ⚠️  After filling in the values above, delete this comment block.

// ─── Form Handler ────────────────────────────────────────────────
(function() {
    "use strict";

    var form = document.getElementById("email-capture-form");
    if (!form) return;  // not on a page with the form

    var btn  = document.getElementById("email-submit-btn");
    var msg  = document.getElementById("email-msg");
    var input = document.getElementById("email-input");

    form.addEventListener("submit", function(e) {
        e.preventDefault();

        var email = input.value.trim();
        if (!email) return;

        // --- Check config ---
        if (EMAILJS_PUBLIC_KEY.indexOf("YOUR_") === 0) {
            msg.textContent = "Email service not configured yet.";
            msg.className = "email-capture__msg email-capture__msg--error";
            return;
        }

        // --- Loading state ---
        btn.disabled = true;
        btn.textContent = "Sending…";
        msg.textContent = "";
        msg.className = "email-capture__msg";

        // --- Init EmailJS on first use ---
        if (typeof emailjs !== "undefined") {
            emailjs.init(EMAILJS_PUBLIC_KEY);
        }

        // --- Send via EmailJS ---
        emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {
            email: email
        }).then(function() {
            // Success → redirect to thank-you page
            window.location.href = "/thanks.html";
        }, function(error) {
            // Failure → show message, re-enable button
            btn.disabled = false;
            btn.textContent = "Get the Kit";
            msg.textContent = "Something went wrong. Please try again.";
            msg.className = "email-capture__msg email-capture__msg--error";
            console.error("EmailJS error:", error);
        });
    });
})();
