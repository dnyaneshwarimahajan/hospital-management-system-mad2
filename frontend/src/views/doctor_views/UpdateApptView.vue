<template>
  <div class="container1">

    <h3>Update Patient History {{ patientName }}</h3>

    <div v-if="errorMsg" style="color:red; text-align:center; margin-bottom:8px;">{{ errorMsg }}</div>
    <div v-if="successMsg" style="color:green; text-align:center; margin-bottom:8px;">{{ successMsg }}</div>

    <div>
      <label>Diagnosis</label><br>
      <input class="input" v-model="form.diagnosis" required />
    </div>

    <div>
      <label>Prescription</label><br>
      <textarea class="input" v-model="form.prescription" rows="4"></textarea>
    </div>

    <div>
      <label>Treatment</label><br>
      <textarea class="input" v-model="form.treatment" rows="4"></textarea>
    </div>

    <div>
      <button @click="save" :disabled="loading">
        {{ loading ? 'Saving' : 'Save' }}
      </button>
      <a class="back-link" @click="$router.push('/doctor')">Back</a>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const BASE = "https://hms-backend-cvcn.onrender.com";

const appointmentId = route.params.id;
const patientName = ref("");
const errorMsg = ref("");
const successMsg = ref("");
const loading = ref(false);

const form = ref({
  diagnosis: "",
  prescription: "",
  treatment: ""
});

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

async function fetchAppointment() {
  try {
    const res = await fetch(`${BASE}/api/doctor/appointment/${appointmentId}/detail`, {
      headers: authHeaders(),
    });
    const data = await res.json();
    patientName.value = data.patient || "";
    if (data.treatment) {
      form.value.diagnosis    = data.treatment.diagnosis    || "";
      form.value.prescription = data.treatment.prescription || "";
      form.value.treatment    = data.treatment.treatment    || "";
    }
  } catch (err) {
    console.error("Failed to load appointment:", err);
  }
}

async function save() {
  errorMsg.value   = "";
  successMsg.value = "";

  if (!form.value.diagnosis || !form.value.treatment) {
    errorMsg.value = "Diagnosis and Treatment are required.";
    return;
  }

  loading.value = true;

  try {
    const res = await fetch(`${BASE}/api/doctor/appointment/${appointmentId}/treatment`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        diagnosis:    form.value.diagnosis,
        prescription: form.value.prescription,
        treatment:    form.value.treatment
      })
    });
    const data = await res.json();
    if (res.ok) {
      successMsg.value = "Saved successfully! Redirecting...";
      setTimeout(() => router.push("/doctor"), 1200);
    } else {
      errorMsg.value = data.message || "Failed to save.";
    }
  } catch (err) {
    errorMsg.value = "Network error: " + err.message;
  } finally {
    loading.value = false;
  }
}

onMounted(fetchAppointment);
</script>

<style scoped>
.container1 {
  max-width: 380px;
  margin: auto;
  margin-top: 100px;
  background-color: #19b39e4a;
  padding: 26px;
}

label {
  text-align: center;
  margin-left: 40%;
}

.container1 h3 {
  text-align: center;
  margin-bottom: 4px;
}

button {
  width: 50%;
  border-radius: 5%;
  margin-left: 25%;
  margin-top: 14px;
  background-color: #3b95e38a;
  border: 1px solid #ccc;
  padding: 6px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input {
  margin-left: 25%;
  margin-bottom: 4px;
  border-radius: 6px;
  padding: 8px;
  width: 100%;
  box-sizing: border-box;
}

.back-link {
  display: block;
  text-align: center;
  margin-top: 18px;
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
  cursor: pointer;
}
</style>