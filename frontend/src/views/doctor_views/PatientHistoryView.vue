<template>
  <div class="page">

    <a class="back-btn" @click="goBack">back</a>

    <template v-if="role === 'admin'">
      <h2 class="header">Patient History</h2>
      <p><strong>Admin Name:</strong> {{ viewerName }}</p>
      <p><strong>Patient Name:</strong> {{ patient.name }}</p>
    </template>
    <template v-else>
      <h2 class="header">Patient History</h2>
      <p><strong>Patient Name:</strong> {{ patient.name }}</p>
    </template>

    <br />

    <div v-if="role === 'patient'" style="margin-bottom: 12px;">
      <button class="export-btn" @click="exportCSV" :disabled="exporting">
        {{ exporting ? 'Exporting.' : '⬇ Export My History as CSV' }}
      </button>
      <span v-if="exportMsg" class="export-msg">{{ exportMsg }}</span>
    </div>

    <div class="table-box">
      <table class="table">
        <thead>
          <tr>
            <th>Visit No.</th>
            <th v-if="role === 'doctor' || role === 'admin'">Patient Name</th>
            <th>Visit Type</th>
            <th>Doctor Name</th>
            <th>Department</th>
            <th>Diagnosis</th>
            <th>Prescription</th>
            <th>Medicines</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="history.length">
            <tr v-for="(h, index) in history" :key="index">
              <td>{{ index + 1 }}.</td>
              <td v-if="role === 'doctor' || role === 'admin'">{{ h.patient_name || '-' }}</td>
              <td>In-person</td>
              <td>{{ h.doctor_name || '-' }}</td>
              <td>{{ h.department_name || '-' }}</td>
              <td>{{ h.treatment?.diagnosis || '-' }}</td>
              <td>{{ h.treatment?.treatment || '-' }}</td>
              <td>{{ h.treatment?.prescription || '-' }}</td>
              <td>{{ h.status || '-' }}</td>
            </tr>
          </template>
          <template v-else>
            <tr>
              <td colspan="9" class="small">No visits recorded.</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route  = useRoute();
const BASE   = "https://hms-backend-cvcn.onrender.com";

const role       = ref(localStorage.getItem("role") || "");
const viewerName = ref(localStorage.getItem("name") || ""); 

const patient   = ref({ name: "" });
const history   = ref([]);
const exporting = ref(false);
const exportMsg = ref("");

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

function goBack() {
  if (role.value === "doctor")
   router.push("/doctor");
  else if (role.value === "patient") 
    router.push("/patient");
  else if (role.value === "admin")   
    router.push("/admin");
  else                               
    router.push("/");
}

async function fetchHistory() {
  const patientId = route.params.id;

  if (!patientId && role.value !== "patient") {
    console.error("No patient ID in route params");
    return;
  }

  try {
    let url = "";
    if (role.value === "doctor") {
      url = `${BASE}/api/doctor/patient/${patientId}/history`;
    } else if (role.value === "admin") {
      url = `${BASE}/api/admin/patient/${patientId}/history`;
    } else {
      url = `${BASE}/api/patient/history`; 
    }

    const res  = await fetch(url, { headers: authHeaders() });

    if (!res.ok) {
      console.error(`History fetch failed: ${res.status} ${res.statusText}`);
      return;
    }

    const data = await res.json();
    patient.value = data.patient || { name: "-" };
    history.value = data.history || [];
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}

async function exportCSV() {
  exporting.value = true;
  exportMsg.value = "";
  try {
    const res = await fetch(`${BASE}/api/export-csv`, {
      method: "POST",
      headers: authHeaders(),
    });
    if (res.ok) {
      exportMsg.value = "Export started! You will receive an email shortly.";
    } else {
      exportMsg.value = "Export failed. Please try again.";
    }
  } catch (err) {
    exportMsg.value = "Something went wrong.";
    console.error("Export error:", err);
  } finally {
    exporting.value = false;
  }
}

onMounted(fetchHistory);
</script>

<style scoped>
.page {
  max-width: 1000px;
  margin: 20px auto;
  background: #eaf3f7cd;
  padding: 20px;
  margin-left: 20%;
}

.back-btn {
  float: right;
  background-color: rgb(2, 33, 33);
  color: white;
  border: 1px solid;
  padding: 5px 12px;
  border-radius: 6px;
  text-decoration: none;
  cursor: pointer;
}

.header {
  border-bottom: 1px solid #111;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.table-box {
  border: 2px solid #111;
  padding: 15px;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 8px;
  border-bottom: 1px solid #ccc;
}

.table th {
  text-align: left;
  font-weight: 600;
}

.small {
  color: #666;
}

.export-btn {
  background-color: rgb(2, 33, 33);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.export-msg {
  margin-left: 12px;
  font-size: 14px;
  color: #2a6b2a;
}
</style>
