export async function onRequestPost(context) {
  const { request, env } = context;

  // Parse JSON body
  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: 'Invalid request body' }, 400);
  }

  const { name, email, message, recaptchaToken } = body;

  // Basic input validation
  if (!name || !email || !message || !recaptchaToken) {
    return jsonResponse({ error: 'All fields are required' }, 400);
  }

  if (name.length > 200 || email.length > 254 || message.length > 5000) {
    return jsonResponse({ error: 'Input exceeds allowed length' }, 400);
  }

  // Verify reCAPTCHA token server-side
  const recaptchaVerify = await fetch('https://www.google.com/recaptcha/api/siteverify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `secret=${encodeURIComponent(env.RECAPTCHA_SECRET_KEY)}&response=${encodeURIComponent(recaptchaToken)}`,
  });

  const recaptchaResult = await recaptchaVerify.json();

  if (!recaptchaResult.success) {
    return jsonResponse({ error: 'CAPTCHA verification failed. Please try again.' }, 400);
  }

  // Send email via Resend
  const emailPayload = {
    from: env.CONTACT_FROM_EMAIL,
    to: [env.CONTACT_TO_EMAIL],
    reply_to: email,
    subject: `New contact form submission from ${name}`,
    html: `
      <h2>New Contact Form Submission</h2>
      <p><strong>Name:</strong> ${escapeHtml(name)}</p>
      <p><strong>Email:</strong> ${escapeHtml(email)}</p>
      <p><strong>Message:</strong></p>
      <p style="white-space:pre-wrap;">${escapeHtml(message)}</p>
    `,
  };

  const resendResponse = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(emailPayload),
  });

  if (!resendResponse.ok) {
    const err = await resendResponse.text();
    console.error('Resend error:', err);
    return jsonResponse({ error: 'Failed to send message. Please try again or email support@zironsec.com directly.' }, 502);
  }

  return jsonResponse({ success: true }, 200);
}

function jsonResponse(data, status) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
