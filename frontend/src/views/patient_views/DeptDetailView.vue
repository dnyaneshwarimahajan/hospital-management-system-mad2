<template>
  <div class="page">
    <div class="header">
      <h2>Department of {{ dept.dept_name }}</h2>
      <div class="actions">
        <a class="btn back" @click="$router.push('/patient')">Back</a>
      </div>
    </div>

    <div class="container">

      <div class="section overview">
        <h3 style="margin-top:0; margin-bottom:8px;">Overview</h3>
        <p>
          {{ dept.description ||
            "This department is dedicated to the diagnosis, treatment and care of patients. It houses a team of specialized doctors and support staff who work together to provide comprehensive care." }}
        </p>
      </div>

      <div class="section">
        <h4 style="margin-bottom:10px;">Doctors' list</h4>

        <div class="doctors-box">
          <template v-if="doctors.length">
            <div class="doctor-row" v-for="d in doctors" :key="d.id">
              <div>
                <div class="doctor-left">Dr. {{ d.name }}</div>
                <div class="doctor-meta">{{ d.email }} • {{ d.contact_no || '-' }}</div>
                <div v-if="d.blacklisted" class="small-note">
                  Status: <strong style="color:#2c0202;">BLACKLISTED</strong>
                </div>
              </div>

              <div class="doctor-actions">
                <a class="btn btn-light" @click="checkAvailability(d.id)">Check availability</a>
                <a class="btn btn-primary" @click="viewDetails(d.id)">View details</a>
              </div>
            </div>
          </template>
          <p v-else class="small-note">No doctors currently listed in this department.</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const BASE = "https://hms-backend-cvcn.onrender.com";

const deptId = route.params.id;
const dept = ref({ dept_name: "", description: "" });
const doctors = ref([]);

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

async function fetchDepartmentDetail() {
  try {
    const res = await fetch(`${BASE}/api/patient/department/${deptId}`, {
      headers: authHeaders(),
    });
    const data = await res.json();
    dept.value = data.department || {};
    doctors.value = data.doctors || [];
  } catch (err) {
    console.error("Failed to load department detail:", err);
  }
}

function checkAvailability(doctorId) {
  router.push(`/book-appointment/${doctorId}`);
}

function viewDetails(doctorId) {
  router.push(`/doctor-detail/${doctorId}`);
}

onMounted(fetchDepartmentDetail);
</script>

<style scoped>
.page {
  max-width: 60%;
  margin: 20px auto;
  padding: 0 15px;
  background: #fbfbfbc7;
  margin-left: 10%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ddd;
}

.container {
  padding-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: #2f0303;
}

.btn {
  padding: 6px 12px;
  border-radius: 5px;
  text-decoration: none;
  font-size: 0.9rem;
  display: inline-block;
  cursor: pointer;
}

.history {
  background-color: #052c2fe2;
  color: white;
  font-weight: 700;
}

.back {
  background-color: #2f0303;
  color: white;
  font-weight: 700;
}

.btn-primary {
  border: 1px solid #000;
  background-color: #2f0303;
  color: rgb(255, 255, 255);
  font-weight: 700;
}

.btn-light {
  border: 1px solid #ccc;
  background-color: #052c2fe2;
  color: white;
  font-weight: 700;
}

.section {
  margin: 20px 0;
}

.overview {
  margin-bottom: 10px;
  font-size: 0.95rem;
}

.doctors-box {
  border: 1px solid #ddd;
  padding: 12px;
  border-radius: 6px;
}

.doctor-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 10px;
  background-color: #92f7f2b2;
}

.doctor-left {
  font-weight: 600;
}

.doctor-meta {
  font-size: 0.85rem;
  color: #666;
}

.doctor-actions {
  display: flex;
  gap: 8px;
}

.small-note {
  font-size: 0.85rem;
  color: #666;
}
</style>