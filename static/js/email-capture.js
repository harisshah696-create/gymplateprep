// ─── EmailJS Configuration ───────────────────────────────────────

var EMAILJS_PUBLIC_KEY  = "AC6isIKtp8Qy8JXXK";
var EMAILJS_SERVICE_ID  = "service_xr3rt13";
var EMAILJS_TEMPLATE_ID = "template_l7ho90d";

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
