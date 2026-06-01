<template>
  <div class="container">
    <div class="row">
      <div class="left">
        <h3 class="h3">Dr. {{ doctor.name }}</h3>
        <div class="meta">
          {{ doctor.qualifications || "MBBS, MD" }} ·
          {{ doctor.specialty || doctor.department || '-' }}
        </div>

        <div class="small">
          <strong>{{ doctor.years_experience || "1" }} Years Experience Overall</strong>
          <div v-if="doctor.years_specialist">
            ({{ doctor.years_specialist }} years as specialist)
          </div>
        </div>

        <div class="bio">
          {{ doctor.bio || `Dr. ${doctor.name} is an experienced doctor in their specialty. Add a short bio from the DB to show the clinician's background and areas of interest.` }}
        </div>

        <div class="actions">
          <a class="btn avail" @click="$router.push(`/book-appointment/${doctor.id}`)">
            Check availability
          </a>
          <a class="back-link" @click="$router.go(-1)">Back</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const BASE = "import.meta.env.VITE_API_BASE_URL";
const doctorId = route.params.id;

const doctor = ref({
  name: "",
  qualifications: "",
  specialty: "",
  department: "",
  years_experience: "",
  years_specialist: "",
  bio: "",
  id: null
});

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

async function fetchDoctorDetail() {
  try {
    const res = await fetch(
      `${BASE}/api/patient/doctors/search?q=`,
      { headers: authHeaders() }
    );
    const data = await res.json();
    const found = (data.doctors || []).find(d => d.id == doctorId);
    if (found) doctor.value = found;
  } catch (err) {
    console.error("Failed to load doctor detail:", err);
  }
}

onMounted(fetchDoctorDetail);
</script>

<style scoped>
.container {
  max-width: 820px;
  margin: 20px auto;
  padding: 10px;
  background-color: white;
  border-radius: 6px;
}

.row {
  align-items: flex-start;
  background-color: #92f7f2b2;
  padding: 12px;
  border-radius: 6px;
}

.left {
  flex: 1;
}

.h3 {
  margin: 0 0 6px 0;
  font-size: 1.1rem;
}

.meta {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 6px;
}

.bio {
  margin-top: 10px;
  line-height: 1.4;
  font-size: 0.95rem;
}

.small {
  color: #777;
  font-size: 0.85rem;
}

.actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn {
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.9rem;
  border: 1px solid #ccc;
  background: #f9f9f9;
  color: #111;
  cursor: pointer;
}

.avail {
  background-color: #052c2fe2;
  color: white;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 6px;
}

.back-link {
  display: block;
  text-align: center;
  margin-top: 18px;
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
  margin-left: 4px;
  cursor: pointer;
}

.btn-outline {
  background: #fff;
  border: 1px solid #ccc;
  color: #111;
}
</style>