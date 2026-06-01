<template>
  <div class="container">
    <div class="card">
      <h2 class="admin"> Admin Dashboard</h2>
      <div class="user-meta"> Welcome {{ adminName }} </div>
    </div>

    <div class="summary">

      <div class="card one">

        <h4>Summary</h4>
        <div class="sum-contain">
          <div class="card doc">
            <strong>{{ filteredDoctors.length }}</strong> 
            <div class="muted">Doctors</div>
          </div>

          <div class="card rest">
            <strong>{{ filteredPatients.length }}</strong>
            <div class="muted">Patients</div>
          </div>

          <div class="card rest">
            <strong>{{ appointments.length }}</strong>
            <div class="muted">Appointments shown</div>
          </div>

        </div>
      </div>

      <div class="create_doc card">
        <RouterLink to="/create-doctor" class="btn btn_create">Create Doctor </RouterLink>
      </div>
    </div>

    <div class="card">
      <h4>Registered Doctors</h4>
     <div v-if="doctors.length">
        <div class="user-row" v-for="d in filteredDoctors" :key="d.id">
          <div style="display:inline-block;">
            <div class="user-left">{{ d.name }}</div>
            <div class="user-meta">
              {{ d.email }} • {{ d.contact_no || '-' }}
            </div>
            <div class="user-meta">
              Dept: {{ d.department || '-' }}
              <span v-if="d.blacklisted" class="badge">BLACKLISTED</span>
            </div>
          </div>

          <div class="btn_edit">
            <RouterLink :to="`/edit-doctor/${d.id}`" class="btn edit">Edit</RouterLink>

            <button class="btn delete" @click="deleteDoctor(d.id)">Delete</button>

            <button class="btn" :class="d.blacklisted ? 'unblock' : 'black' "@click="toggleBlacklist(d)">
              {{ d.blacklisted ? 'Unblock' : 'Blacklist' }}
            </button>
          </div>
        </div>
      </div>

      <p v-else class="muted">No registered doctors.</p>
    </div>

    <div class="card" style="margin-top:14px;">
      <h4>Registered Patients</h4>

      <div v-if="patients.length">
        <div class="user-row" v-for="p in filteredPatients" :key="p.id">
          <div>
            <div class="user-left">{{ p.name }}</div>
            <div class="user-meta">{{ p.email }}</div>
            <div class="user-meta">{{ p.contact_no || '-' }}</div>

            <span v-if="p.blacklisted" class="badge">BLACKLISTED</span>
          </div>

          <div class="btn_edit">

            <RouterLink :to="`/edit-patient/${p.id}`" class="btn edit">Edit</RouterLink>

            <button class="btn delete" @click="deletePatient(p.id)">Delete</button>

            <button class="btn" :class="p.blacklisted ? 'unblock' : 'black'" @click="toggleBlacklist(p)">
              {{ p.blacklisted ? 'Unblock' : 'Blacklist' }}
            </button>
          </div>
        </div>
      </div>

      <p v-else class="muted">No registered patients.</p>
    </div>

    
    <div class="card" style="margin-top:14px;">
      <h4 style="margin-bottom:7px;">Upcoming Appointments</h4>

      <div style="overflow:auto">
        <table class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Department</th>
              <th>When</th>
              <th>History</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!appointments.length">
              <td colspan="6" class="muted">No upcoming appointments</td>
            </tr>

            <tr v-for="(a, index) in appointments" :key="a.id">
              <td>{{ index + 1 }}</td>
              <td>{{ a.patient }}</td>
              <td>{{ a.doctor || '-' }}</td>
              <td>{{ a.department || '-' }}</td>
              <td>
                {{ a.date }} /
                {{ a.time === 'slot1' ? '8:00 AM - 12:00 PM' : '4:00 PM - 9:00 PM' }}
              </td>
              <td>
                <RouterLink :to="`/patient-history/${a.patient_id}`" class="btn btn_create">View</RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <RouterLink to="/past-appointments" class="btn btn_create">View Past Appointments</RouterLink>
    </div>
  </div>
</template>

<script setup>
const BASE = "https://hms-backend-cvcn.onrender.com"
// const BASE = "http://127.0.0.1:5000"

import { ref, onMounted, computed, onActivated } from "vue";

import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

const adminName = ref("Admin");
const doctors = ref([]);
const patients = ref([]);
const appointments = ref([]);


const searchQuery = computed(() => route.query.q || "");

const filteredDoctors = computed(() =>
  doctors.value.filter(d => {
    const q = searchQuery.value.toLowerCase();
    return (
      d.name.toLowerCase().includes(q) ||
      (d.department  || "").toLowerCase().includes(q) ||
      (d.email       || "").toLowerCase().includes(q) ||
      (d.contact_no  || "").toLowerCase().includes(q)
    );
  })
);

const filteredPatients = computed(() =>
  patients.value.filter(p => {
    const q = searchQuery.value.toLowerCase();
    return (
      p.name.toLowerCase().includes(q) ||
      (p.email      || "").toLowerCase().includes(q) ||
      (p.contact_no || "").toLowerCase().includes(q)
    );
  })
);


async function apiRequest(url, method = "GET", body = null) {
  const token = localStorage.getItem("token");
  const options = {
    method,
    headers: { "Authentication-Token": token, "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : null,
  };
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return method === "GET" ? res.json() : res;
}

async function fetchDashboard() {
  try {
    const data = await apiRequest(`${BASE}/api/admin/dashboard`);
    doctors.value = data.doctors;
    patients.value = data.patients;
    appointments.value = data.appointments;
  } catch (err) {
    console.error(err);
  }
}

onMounted(fetchDashboard);

onActivated(fetchDashboard);

const deleteDoctor = async (id) => {
  if (!confirm("Delete this doctor?")) return;
  await apiRequest(`${BASE}/api/admin/delete-doctor/${id}`, "DELETE");
  fetchDashboard();
};

const deletePatient = async (id)=> {
  if (!confirm("Delete this patient?")) return;
  await apiRequest(`${BASE}/api/admin/delete-patient/${id}`, "DELETE");
  fetchDashboard();
};

const toggleBlacklist = async (user) =>{
  const url = user.blacklisted
    ? `${BASE}/api/admin/unblacklist/${user.id}`
     : `${BASE}/api/admin/blacklist/${user.id}`;
  await apiRequest(url, "PUT");
  fetchDashboard();
};
</script>

<style scoped>
* 
{ 
  margin: 0; 
  padding:0; 
  box-sizing:border-box; 
}

.container { 
  max-width: 1100px;
   margin: 20px auto; 
   padding: 18px; }

.card { 
  background:#fbfbfbc7; 
  padding:16px; 
  border-radius: 8px; 
  border: 1px solid #e5e7eb; 
  margin-bottom: 16px;}

.card h4{ 
  color: #61052d; 
}

.user-row 
{ display: flex; 
  justify-content: 
  space-between; 
  padding: 12px 10px; 
  border-bottom: 5px solid #b4f0f0ab; 
}
.user-row:last-child { 
  border-bottom: none;
 }
.user-left { 
  font-weight: 600; 
  font-size: 1.05rem; 
  font-style:italic; color:#054145; 
}
.user-meta 
{ color:#3559a1;
   font-size: 0.9rem;
    margin-top: 3px; 
  }
.btn { 
  padding: 8px 12px; 
  border-radius: 8px; 
  border: none;
   cursor: pointer; 
   font-weight: 600; 
  font-size: 0.95rem; }
.edit
{ background-color:#5b9094; 
  color: #111827; }
.delete{ 
  background-color: #e66969b8;
   color:#2f0303; }

.black
{ background-color: #05132f9e; }

.unblock{ 
  background-color: #066f77c3; }
.btn_create{
   background-color: #052c2fe2;
    color: white; }
.muted { 
  color: #6b7280; 
  font-size: 0.9rem; 
}
.summary{ 
  display:flex;
  gap:12px;
  flex-wrap:wrap;
  margin-bottom:14px; 
}
.one
{ flex:1;
  min-width:220px
 }
.doc{ 
  flex:1;
  min-width:120px;
 }
.rest{ 
  flex:1;
  min-width:120px

}
.create_doc{ 
  flex:1;
  min-width:320px 
}
.badge{ 
  color:#2f0303;
  font-weight:600;
  margin-left:8px
   }
</style>
