

<template>
  <div>
    <div class="card">
      <h2 class="admin">Patient Dashboard</h2>
      <div class="user-meta">Welcome, {{ patientName }}</div>
    </div>

    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <h3 style="padding-bottom:0;">Departments</h3>
        <input class="search-input" style="width:240px;" type="search" placeholder="Search department..." v-model="deptSearch" />
      </div>
      <div class="tiles">
        <template v-if="filteredDepartments.length">
          <div class="tile" v-for="dept in filteredDepartments" :key="dept.id">
            <h4>{{ dept.dept_name }}</h4>
            <div class="small">{{ dept.description || '-' }}</div>
            <div style="margin-top:10px;">
              <a class="btn btn-primary" @click="router.push(`/doctors/${dept.id}`)">View Doctors</a>
            </div>
          </div>
        </template>
        <p v-else class="empty">No departments found.</p>
      </div>
    </div>

    <div class="card">
      <h3>Upcoming Appointments</h3>
      <template v-if="upcomingAppointments.length">
        <table class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Doctor</th>
              <th>Department</th>
              <th>Date</th>
              <th>Time</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(a, i) in upcomingAppointments" :key="a.id">
              <td>{{ i + 1001 }}.</td>
              <td>{{ a.doctor || '-' }}</td>
              <td>{{ a.department || '-' }}</td>
              <td>{{ a.date }}</td>
              <td>{{ a.time === 'slot1' ? '8:00 AM - 12:00 PM' : '4:00 PM - 9:00 PM' }}</td>
              <td class="actions">
                <button class="btn btn-primary" @click="router.push(`/book-appointment/${a.doctor_id}?reschedule=${a.id}`)">Reschedule</button>
                <button class="btn btn-outline cancel" @click="cancelAppointment(a.id)">Cancel</button>
              </td>
            </tr>
          </tbody>
        </table>
      </template>
      <p v-else class="empty">You have no upcoming appointments.</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, computed, onMounted } from "vue";

const router = useRouter();
const BASE = "https://hms-backend-cvcn.onrender.com";

const patientName = ref(localStorage.getItem("name") || "Patient");
const departments = ref([]);
const upcomingAppointments = ref([]);
const deptSearch = ref("");
const today = new Date().toISOString().split("T")[0];

const filteredDepartments = computed(() =>
  departments.value.filter(d =>
    d.dept_name.toLowerCase().includes(deptSearch.value.toLowerCase())
  )
);

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

async function apiFetch(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, { headers: authHeaders(), ...options });
  return res.json();
}

async function fetchDashboard() {
  const data = await apiFetch(`/api/patient/dashboard?t=${Date.now()}`);
  upcomingAppointments.value = data.upcoming_appointments || [];
}

async function fetchDepartments() {
  const data = await apiFetch("/api/patient/departments");
  departments.value = data.departments || [];
}

async function cancelAppointment(id) {
  if (!confirm("Cancel this appointment?")) return;
  await apiFetch(`/api/patient/appointment/${id}/cancel`, { method: "PUT" });
  fetchDashboard();
}

onMounted(() => {
  fetchDashboard();
  fetchDepartments();
});
</script>

<style scoped>
.container 
{ max-width: 90%;
  margin: 20px auto;
   padding: 18px; }

.card {
   background: #fbfbfbc7; 
   padding: 16px; 
   border-radius: 8px; 
   border: 1px solid #e5e7eb; 
   margin-bottom: 16px; }
.card h3 
{ padding-bottom:
   20px; 
   color: #022820ef; }
.card h4 { color: #61052d; }

.user-meta { color: #3559a1; 
  font-size: 0.9rem;
   margin-top: 3px; }
.actions { display: flex;
   gap: 8px; 
   align-items: center; }

.btn {
   padding: 8px 12px; 
   border-radius: 6px;
    border: 0; cursor: pointer; 
    text-decoration: none; 
    color: #fff; 
    font-size: 0.95rem; 
  }
.btn-primary { 
  background: #023636; }
.btn-outline { 
  background: transparent; 
  border: 1px solid #ddd; 
  color: #111; }

.tiles { 
  display: flex;
   gap: 12px;
    flex-wrap: wrap; }
.tile {
   flex: 1 1 30%; 
   max-width: 300px;
    border: 1px solid #f0f0f0; 
    border-radius: 8px; 
    padding: 12px;
     background-color: #29dbdb79; }
.tile h4 { 
  margin: 0 0 6px 0; 
  font-size: 1.02rem; }
.small {
   color: #6b7280; 
   font-size: 0.92rem; }

.table { 
  width: 100%; 
  border-collapse: collapse; 
  margin-top: 8px; 
}
.table th, .table td {
   padding: 10px; 
   border-bottom: 1px solid #eee; 
   text-align: left; 
  }
.table th {
   background: #82efd7b7; 
   font-weight: 700; 
   padding-bottom: 10px; }

.empty { 
  color: #6b7280; 
  font-style: italic; 
  padding: 12px 0;
 }
.cancel { 
  background-color: #e66969b8; 
  color: #2f0303; 
  font-weight: 700; }
.search-input { 
  width: 100%; 
  padding: 9px 12px;
   border-radius: 6px;
    border: 1px solid #d1d5db; 
    font-size: 0.95rem; 
    background: #ffffffcc; }

.modal-overlay {
   position: fixed; 
   inset: 0; 
   background: rgba(0,0,0,0.4);
    display: flex; 
    align-items: center;
     justify-content: center;
      z-index: 999; }
.modal {
   background: #fff;
    padding: 24px; 
    border-radius: 10px;
     width: 380px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
.modal h4 {
   margin-bottom: 12px; 
   color: #022820ef; }
.modal label { 
  display: block;
   font-weight: 600; 
   margin-bottom: 4px; 
   
   color: #054145; }
.modal-input {
   width: 100%; 
   padding: 9px 11px;
    border-radius: 6px;
     border: 1px solid #cdd; 
     font-size: 0.95rem; 
     background: #ffffffcc; }
</style>