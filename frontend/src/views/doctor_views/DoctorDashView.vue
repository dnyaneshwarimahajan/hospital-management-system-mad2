<template>
  <div class="container">

    <div class="section">
      <h2>Welcome Dr. {{ doctor.name }}</h2>
    </div>

    <div class="section">
      <h3>Upcoming Appointments</h3>

      <div v-if="weekAppointments.length">
        <table>
          <thead>
            <tr>
              <th>Sr No.</th>
              <th>Patient</th>
              <th>When</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(a, index) in weekAppointments" :key="a.id">
              <td>{{ index + 1001 }}.</td>
              <td>{{ a.patient }}</td>
              <td>
                {{ a.date }} /
                {{ a.time === 'slot1' ? '8:00 AM - 12:00 PM' : '4:00 PM - 9:00 PM' }}
              </td>
              <td>
                <a class="button update" @click="goToUpdate(a.id)">update</a>
                <button @click="markStatus(a.id, 'completed')">mark as complete</button>
                <button class="cancel" @click="markStatus(a.id, 'cancelled')">Cancel</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-else>No upcoming appointments.</p>

      <hr />
    </div>

    <div class="section">
      <h3>Assigned Patients</h3>

      <div v-if="patients.length">
        <div class="assigned-row" v-for="p in patients" :key="p.id">
          <div>
            <strong>{{ p.name }}</strong><br />
            <small>{{ p.email || '' }}</small>
          </div>
          <div>
            <RouterLink :to="`/patient-history/${p.id}`" class="button update">View History</RouterLink>
          </div>
        </div>
      </div>

      <p v-else>No assigned patients.</p>
    </div>

    <div class="section">
      <p class="avail"> 
        <RouterLink to="/doctor/availability">Provide Availability</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const BASE = "import.meta.env.VITE_API_BASE_URL";

const doctor = ref({ name: "" });
const weekAppointments = ref([]);
const patients = ref([]);

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

async function fetchDashboard() {
  try {
    const res = await fetch(`${BASE}/api/doctor/dashboard`, {
      headers: authHeaders(),
    });
    const data = await res.json();
    doctor.value = data.doctor;
    weekAppointments.value = data.week_appointments;
    patients.value = data.patients;
  } catch (err) {
    console.error("Failed to load dashboard:", err);
  }
}

async function markStatus(appointmentId, status) {
  if (!confirm(`Mark appointment as ${status}?`)) return;
  try {
    await fetch(`${BASE}/api/doctor/appointment/${appointmentId}/status`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({ status }),
    });
    fetchDashboard();
  } catch (err) {
    console.error("Failed to update status:", err);
  }
}

function goToUpdate(appointmentId) {
  router.push(`/doctor/appointment/${appointmentId}/update`);
}

onMounted(fetchDashboard);
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 20px auto;
  padding: 15px;
  background: #fee6e6c7;
}

.section {
  background: #cdf3f979;
  padding: 5px;
  margin-bottom: 4px;
  border-radius: 6px;
}

h2, h3 {
  margin-bottom: 10px;
  font-weight: 600;
}

thead {
  background-color: rgba(255, 255, 255, 0.522);
  border-radius: 7px;
}

.update {
  font-weight: 700;
  background: #023636;
  color: #ddd;
  padding: 6px;
  border-radius: 6px;
}

.cancel {
  font-weight: 700;
  background: #ffa2fdc2;
  color: #250505;
  padding: 6px;
  border-radius: 6px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-weight: 400;
}

th, td {
  padding: 8px;
  text-align: left;
  font-size: 0.95rem;
}

th {
  border-bottom: 1px solid #ddd;
}

tr:not(:last-child) td {
  border-bottom: 1px solid #f0f0f0;
}

a {
  text-decoration: none;
  font-size: 0.9rem;
  display: inline;
  font-weight: 700;
  color: white;
  cursor: pointer;
}

a:hover {
  text-decoration: underline;
}
.assigned-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 0.95rem;
}

.assigned-row small {
  color: #555;
}

.avail {
  display: inline-block;
  margin-left: 5px;
  margin-bottom: 4px;
  border: 1px solid #000;
  padding: 6px;
  border-radius: 6px;
  font-weight: 700;
  background: #023636;
  color: #ddd;
}

button {
  padding: 5px 10px;
  font-size: 0.85rem;
  border-radius: 6px;
  cursor: pointer;
  background-color: #ff9ee094;
  font-weight: 700;
}

button:hover {
  background: #eee;
}

hr {
  margin: 20px 0;
  border: none;
  border-top: 1px solid #e0e0e0;
}
</style>