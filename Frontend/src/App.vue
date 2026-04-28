<script setup>
import { computed, onMounted, ref, watch } from "vue";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
const apiStatus = ref("checking");
const saveStatus = ref("idle");
const emailCheckStatus = ref("idle");
const savedProfileId = ref(null);
const saveError = ref("");
const emailAnalysis = ref(null);

const profile = ref({
  email: "hello@example.com",
  domain: "example.com",
  assessment_answers: {
    mfa_enabled: "unknown",
    password_manager_used: "unknown",
    recovery_email_secured: "unknown",
    forwarding_rules_checked: "unknown",
    backup_codes_stored: "unknown",
    security_activity_reviewed: "unknown",
  },
});

const metricGroups = [
  {
    title: "Account Protection",
    code: "AP",
    metrics: [
      {
        key: "mfa_enabled",
        code: "MFA",
        label: "MFA strength",
        points: 25,
        fix: "Enable app-based MFA or a passkey on the main email account.",
        exposed: "A leaked password can become an account takeover.",
        options: [
          { value: "yes", label: "Strong", code: "S", factor: 1 },
          { value: "unknown", label: "Unknown", code: "U", factor: 0.35 },
          { value: "no", label: "None", code: "N", factor: 0 },
        ],
      },
      {
        key: "password_manager_used",
        code: "PW",
        label: "Password uniqueness",
        points: 20,
        fix: "Use a password manager and replace reused passwords, starting with email and recovery accounts.",
        exposed: "One reused password can unlock more than one account.",
        options: [
          { value: "yes", label: "Unique", code: "U", factor: 1 },
          { value: "unknown", label: "Unknown", code: "?", factor: 0.35 },
          { value: "no", label: "Reused", code: "R", factor: 0 },
        ],
      },
    ],
  },
  {
    title: "Recovery Risk",
    code: "RR",
    metrics: [
      {
        key: "recovery_email_secured",
        code: "REC",
        label: "Recovery methods",
        points: 20,
        fix: "Remove old recovery emails and phone numbers, then protect the ones that remain.",
        exposed: "A weak recovery route can reset your main email.",
        options: [
          { value: "yes", label: "Protected", code: "P", factor: 1 },
          { value: "unknown", label: "Unknown", code: "U", factor: 0.35 },
          { value: "no", label: "Weak", code: "W", factor: 0 },
        ],
      },
      {
        key: "backup_codes_stored",
        code: "BC",
        label: "Backup codes",
        points: 10,
        fix: "Generate backup codes and store them somewhere safe outside the same email account.",
        exposed: "Recovery can fail if the only backup is inside the account you lose.",
        options: [
          { value: "yes", label: "Stored", code: "S", factor: 1 },
          { value: "unknown", label: "Unknown", code: "U", factor: 0.35 },
          { value: "no", label: "Missing", code: "M", factor: 0 },
        ],
      },
    ],
  },
  {
    title: "Mailbox Persistence",
    code: "MP",
    metrics: [
      {
        key: "forwarding_rules_checked",
        code: "FWD",
        label: "Forwarding and app access",
        points: 15,
        fix: "Look for unknown forwarding addresses, filters, connected apps, and app passwords.",
        exposed: "A quiet inbox rule can keep leaking mail after the password changes.",
        options: [
          { value: "yes", label: "Reviewed", code: "R", factor: 1 },
          { value: "unknown", label: "Unknown", code: "U", factor: 0.35 },
          { value: "no", label: "Unchecked", code: "N", factor: 0 },
        ],
      },
      {
        key: "security_activity_reviewed",
        code: "ACT",
        label: "Recent activity",
        points: 10,
        fix: "Review recent login locations, active sessions, OAuth apps, and devices.",
        exposed: "Old sessions and connected apps can keep access alive.",
        options: [
          { value: "yes", label: "Reviewed", code: "R", factor: 1 },
          { value: "unknown", label: "Unknown", code: "U", factor: 0.35 },
          { value: "no", label: "Unchecked", code: "N", factor: 0 },
        ],
      },
    ],
  },
];

const metrics = computed(() => metricGroups.flatMap((group) => group.metrics));

const score = computed(() =>
  metrics.value.reduce((total, metric) => {
    const option = selectedOption(metric);
    return total + Math.round(metric.points * option.factor);
  }, 0),
);

const riskLevel = computed(() => {
  if (score.value >= 80) return "Low exposure";
  if (score.value >= 55) return "Moderate exposure";
  if (score.value >= 35) return "High exposure";
  return "Critical exposure";
});

const vector = computed(() => {
  const parts = metrics.value.map((metric) => `${metric.code}:${selectedOption(metric).code}`);
  return `SME:1.0/${parts.join("/")}`;
});

const openIssues = computed(() =>
  metrics.value.filter((metric) => profile.value.assessment_answers[metric.key] !== "yes"),
);
const topFixes = computed(() => openIssues.value.slice(0, 3));

const publicSignals = computed(() => emailAnalysis.value?.checks || []);
const publicSignalSummary = computed(() => {
  if (!publicSignals.value.length) return "Run the email check to populate public signals.";
  const passed = publicSignals.value.filter((check) => check.status === "pass").length;
  return `${passed} of ${publicSignals.value.length} public signals passed.`;
});

const attackPath = computed(() => {
  const issue = topFixes.value[0];

  if (!issue) {
    return {
      title: "No obvious account takeover path",
      why: "The selected account controls cover the main email takeover paths in this calculator.",
      fix: "Keep recovery settings current and re-check after major account changes.",
    };
  }

  const selected = selectedOption(issue);
  const uncertain = selected.value === "unknown";
  const prefix = uncertain ? "Unknown" : "Weak";

  return {
    title: `${prefix} ${issue.label.toLowerCase()}`,
    why: issue.exposed,
    fix: issue.fix,
  };
});

const exposureItems = computed(() => [
  {
    label: "Identity anchor",
    value: profile.value.email || "No email set",
  },
  {
    label: "Derived domain",
    value: profile.value.domain || "No domain connected",
  },
]);

watch(
  () => profile.value.email,
  (email) => {
    const domain = email.split("@")[1]?.trim().toLowerCase();

    if (domain && (!profile.value.domain || profile.value.domain === "example.com")) {
      profile.value.domain = domain;
    }
  },
);

function selectedOption(metric) {
  const value = profile.value.assessment_answers[metric.key] || "unknown";
  return metric.options.find((option) => option.value === value) || metric.options[1];
}

async function saveProfile() {
  saveStatus.value = "saving";
  saveError.value = "";

  const answers = profile.value.assessment_answers;

  try {
    const response = await fetch(`${apiBaseUrl}/profiles/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...profile.value,
        mfa_enabled: answers.mfa_enabled === "yes",
        password_manager_used: answers.password_manager_used === "yes",
        recovery_email_secured: answers.recovery_email_secured === "yes",
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(formatApiError(data));
    }

    savedProfileId.value = data.id;
    saveStatus.value = "saved";
  } catch (error) {
    saveError.value = error.message || "The profile could not be saved.";
    saveStatus.value = "failed";
  }
}

async function checkEmail() {
  emailCheckStatus.value = "checking";

  try {
    const response = await fetch(`${apiBaseUrl}/email/check/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: profile.value.email,
      }),
    });

    if (!response.ok) {
      throw new Error("Email check failed.");
    }

    emailAnalysis.value = await response.json();

    if (emailAnalysis.value.domain && (!profile.value.domain || profile.value.domain === "example.com")) {
      profile.value.domain = emailAnalysis.value.domain;
    }

    emailCheckStatus.value = "done";
  } catch {
    emailCheckStatus.value = "failed";
  }
}

function formatApiError(data) {
  if (!data || typeof data !== "object") {
    return "The API returned an unexpected error.";
  }

  return Object.entries(data)
    .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(", ") : messages}`)
    .join(" ");
}

onMounted(async () => {
  try {
    const response = await fetch(`${apiBaseUrl}/health/`);
    apiStatus.value = response.ok ? "online" : "unreachable";
  } catch {
    apiStatus.value = "unreachable";
  }
});
</script>

<template>
  <main class="shell">
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">SecureMe Calculator</p>
        <h1>Email exposure vector</h1>
        <p class="lede">
          Score an email identity with public domain signals and account-control metrics. Change a value, watch the exposure shift.
        </p>
      </div>

      <div class="score-panel">
        <span class="score-label">{{ riskLevel }}</span>
        <strong>{{ score }}</strong>
        <span class="score-max">Security score / 100</span>
      </div>
    </section>

    <section class="workspace calculator-layout">
      <section class="scan-panel metric-panel">
        <div class="panel-heading">
          <div>
            <p class="section-kicker">Target</p>
            <h2>Email identity</h2>
          </div>
          <span class="api-pill" :class="apiStatus">{{ apiStatus }}</span>
        </div>

        <div class="target-grid">
          <label>
            Email
            <input v-model="profile.email" type="email" autocomplete="email" />
          </label>

          <label>
            Domain
            <input v-model="profile.domain" type="text" autocomplete="url" />
          </label>
        </div>

        <section v-for="group in metricGroups" :key="group.code" class="metric-group">
          <div class="metric-group-heading">
            <span>{{ group.code }}</span>
            <h3>{{ group.title }}</h3>
          </div>

          <article v-for="metric in group.metrics" :key="metric.key" class="metric-row">
            <div class="metric-copy">
              <span>{{ metric.code }}</span>
              <strong>{{ metric.label }}</strong>
              <small>{{ metric.points }} max points</small>
            </div>

            <div class="metric-options" :aria-label="metric.label">
              <button
                v-for="option in metric.options"
                :key="option.value"
                type="button"
                :class="{ selected: profile.assessment_answers[metric.key] === option.value }"
                @click="profile.assessment_answers[metric.key] = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </article>
        </section>

        <button class="primary-action" type="button" @click="checkEmail">
          {{ emailCheckStatus === "checking" ? "Checking email..." : "Check public email signals" }}
        </button>

        <button class="secondary-action" type="button" @click="saveProfile">
          {{ saveStatus === "saving" ? "Saving..." : "Save calculator result" }}
        </button>

        <p v-if="saveStatus === 'saved'" class="save-message">
          Saved profile #{{ savedProfileId }} to Supabase.
        </p>
        <p v-if="saveStatus === 'failed'" class="save-message error">
          {{ saveError }}
        </p>
        <p v-if="emailCheckStatus === 'failed'" class="save-message error">
          Email check failed. Confirm the backend is running and try again.
        </p>
      </section>

      <aside class="insight-panel result-panel">
        <div>
          <p class="section-kicker">Result</p>
          <h2>Exposure summary</h2>
        </div>

        <section class="attack-path">
          <span>Most likely risk</span>
          <h3>{{ attackPath.title }}</h3>
          <p>{{ attackPath.why }}</p>
          <strong>{{ attackPath.fix }}</strong>
        </section>

        <div class="vector-line">
          <span>Vector</span>
          <code>{{ vector }}</code>
        </div>

        <dl class="exposure-list">
          <div v-for="item in exposureItems" :key="item.label">
            <dt>{{ item.label }}</dt>
            <dd>{{ item.value }}</dd>
          </div>
        </dl>

        <div class="signal-list">
          <p>{{ publicSignalSummary }}</p>
          <div v-for="check in publicSignals" :key="check.key" class="signal-row">
            <span :class="check.status">{{ check.status }}</span>
            <div>
              <strong>{{ check.label }}</strong>
              <small>{{ check.detail }}</small>
            </div>
          </div>
        </div>
      </aside>
    </section>

    <section class="recommendations">
      <div class="panel-heading">
        <div>
          <p class="section-kicker">Next actions</p>
          <h2>Fix these first</h2>
        </div>
        <span>{{ openIssues.length }} open or uncertain</span>
      </div>

      <div class="fix-grid">
        <article v-for="fix in topFixes" :key="fix.key" class="fix-card">
          <span>{{ selectedOption(fix).label }}</span>
          <h3>{{ fix.label }}</h3>
          <p>{{ fix.fix }}</p>
        </article>

        <article v-if="topFixes.length === 0" class="fix-card complete">
          <span>Ready</span>
          <h3>Core posture looks strong</h3>
          <p>Keep MFA on, use unique passwords, and rescan when account recovery settings change.</p>
        </article>
      </div>
    </section>
  </main>
</template>
