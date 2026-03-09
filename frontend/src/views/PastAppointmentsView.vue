<template>
  <div class="container">

    <!-- Header -->
    <div class="card">
      <button class="btn btn_create back-btn" @click="$router.push('/admin')">← Back</button>
      <h2 class="admin">Appointment History</h2>
      <div class="user-meta">Admin — Full appointment records</div>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="filters">
        <input
          v-model="search"
          placeholder="Search by patient or doctor..."
          class="search-input"
        />
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Statuses</option>
          <option value="booked">Booked</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="card" style="margin-top:14px;">
      <h4 style="margin-bottom:10px;">
        All Appointments
        <span class="muted" style="font-weight:400; font-size:0.9rem;">
          ({{ filtered.length }} records)
        </span>
      </h4>

      <div style="overflow:auto">
        <table class="table">
          <thead>
            <tr>
              <th>Visit No.</th>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Date</th>
              <th>Time</th>
              <th>Status</th>
              <th>Diagnosis</th>
              <th>Treatment</th>
              <th>History</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!filtered.length">
              <td colspan="9" class="muted" style="text-align:center; padding:20px;">
                No appointments found.
              </td>
            </tr>
            <tr v-for="(a, index) in filtered" :key="a.id">
              <td>{{ index + 1 }}.</td>
              <td>{{ a.patient }}</td>
              <td>{{ a.doctor }}</td>
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td>
                <span :class="['badge-status', a.status]">{{ a.status }}</span>
              </td>
              <td>{{ a.diagnosis || '-' }}</td>
              <td>{{ a.treatment || '-' }}</td>
              <td>
                <button
                  class="btn btn_create"
                  @click="$router.push(`/patient-history/${a.patient_id}`)"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";

const router       = useRouter();
const BASE         = "http://127.0.0.1:5000";
const appointments = ref([]);
const search       = ref("");
const statusFilter = ref("");

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

async function fetchAppointments() {
  try {
    const res  = await fetch(`${BASE}/api/admin/appointments/all`, { headers: authHeaders() });
    const data = await res.json();
    appointments.value = data.appointments || [];
  } catch (err) {
    console.error("Failed to fetch appointments:", err);
  }
}

const filtered = computed(() => {
  return appointments.value.filter(a => {
    const matchSearch =
      !search.value ||
      a.patient.toLowerCase().includes(search.value.toLowerCase()) ||
      a.doctor.toLowerCase().includes(search.value.toLowerCase());
    const matchStatus = !statusFilter.value || a.status === statusFilter.value;
    return matchSearch && matchStatus;
  });
});

onMounted(fetchAppointments);
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }
.container  { max-width: 1100px; margin: 20px auto; padding: 18px; }
.card       { background: #fbfbfbc7; padding: 16px; border-radius: 8px; border: 1px solid #e5e7eb; margin-bottom: 16px; }
.card h4    { color: #61052d; }
.admin      { color: #054145; margin-top: 6px; }
.user-meta  { color: #3559a1; font-size: 0.9rem; margin-top: 3px; }
.muted      { color: #6b7280; font-size: 0.9rem; }
.back-btn   { margin-bottom: 10px; }

.filters       { display: flex; gap: 12px; flex-wrap: wrap; }
.search-input  { flex: 1; min-width: 200px; padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 0.95rem; }
.filter-select { padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 0.95rem; }

.table            { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
.table th         { background: #054145; color: white; padding: 10px 8px; text-align: left; }
.table td         { padding: 9px 8px; border-bottom: 1px solid #e5e7eb; }
.table tr:hover td { background: #eaf3f7; }

.badge-status           { padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: capitalize; }
.badge-status.booked    { background: #dbeafe; color: #1d4ed8; }
.badge-status.completed { background: #d1fae5; color: #065f46; }
.badge-status.cancelled { background: #fee2e2; color: #991b1b; }

.btn        { padding: 6px 12px; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; font-size: 0.9rem; }
.btn_create { background-color: #052c2fe2; color: white; }
</style>