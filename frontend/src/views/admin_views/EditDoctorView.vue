<template>
  <div class="edit-box">
    <h2>Edit Doctor</h2>

    <div v-if="errorMsg" class="alert error">{{ errorMsg }}</div>
    <div v-if="successMsg" class="alert success">{{ successMsg }}</div>

    <form class="edit-form" @submit.prevent="saveChanges">

      <label>Username</label>
      <input type="text" class="input" v-model="form.username" required />

      <label>Email</label>
      <input type="email" class="input" v-model="form.email" required />

      <label>Password <span class="hint">(leave blank to keep same)</span></label>
      <input type="password" class="input" v-model="form.password" placeholder="Enter new password" />

      <label>Select Department<br>
        <span class="hint">(Leave same if not changing department from existing departments)</span>
      </label>
      <select class="input" v-model="form.department_id" :disabled="!!form.new_department">
        <option value="">-- Select existing department --</option>
        <option v-for="dept in departments" :key="dept.id" :value="dept.id">
          {{ dept.dept_name }}
        </option>
      </select>

      <label>Create New Department<br>
        <span class="hint">(Leave blank if not creating a new department)</span>
      </label>
      <input type="text" class="input" v-model="form.new_department"
        :disabled="!!form.department_id"
        placeholder="Enter new department name" />

      <label>Qualifications</label>
      <input type="text" class="input" v-model="form.qualifications" />

      <label>Contact Number</label>
      <input type="number" class="input" v-model="form.contact_no" />

      <label>Years of Experience</label>
      <input type="number" class="input" v-model="form.years_experience" />

      <button type="submit" class="btn btn-primary form-btn" :disabled="loading">
        {{ loading ? 'Saving' : 'Save Changes' }}
      </button>

    </form>

    <a class="back-link" @click.prevent="$router.push('/admin')">Back to Dashboard</a>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

const BASE = "https://hms-backend-cvcn.onrender.com";
const router = useRouter();
const route  = useRoute();
const id     = route.params.id;

const form = ref({
  username: "",
  email: "",
  password: "",
  department_id: "",
  new_department: "",
  qualifications: "",
  contact_no: "",
  years_experience: "",
});

const departments = ref([]);
const loading     = ref(false);
const errorMsg    = ref("");
const successMsg  = ref("");

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

async function fetchDepartments() {
  try {
    const res = await fetch(`${BASE}/api/admin/create-doctor`, { headers: authHeaders() });
    const data = await res.json();
    departments.value = data.departments || [];
  } catch (err) {
    console.error("Failed to load departments", err);
  }
}

onMounted(async () => {
  await fetchDepartments();
  await fetchDoctor();
});

async function fetchDoctor() {
  try {
    const res  = await fetch(`${BASE}/api/admin/edit-doctor/${id}`, { 
      headers: authHeaders() 
    });
    const data = await res.json();
    form.value.username = data.username || "";
    form.value.email= data.email || "";
    form.value.contact_no = data.contact_no || "";
    form.value.qualifications = data.qualifications || "";
    form.value.years_experience = data.years_experience || "";
    form.value.department_id = data.department_id || "";
  } catch (err) {
    errorMsg.value = "Failed to load doctor data.";
  }
}

async function saveChanges() {
  errorMsg.value = "";
  successMsg.value = "";
  loading.value = true;

  const payload = {
    username:form.value.username || undefined,
    email:form.value.email || undefined,
    password: form.value.password || undefined,
    department_id: form.value.department_id || undefined,
    new_department_name: form.value.new_department || undefined,
    qualifications: form.value.qualifications || undefined,
    contact_no: form.value.contact_no || undefined,
    years_experience: form.value.years_experience || undefined,
  };

  try {
    const res  = await fetch(`${BASE}/api/admin/edit-doctor/${id}`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      errorMsg.value = data.message || `Error ${res.status}`;
    } else {
      successMsg.value = "Doctor updated successfully! Redirecting...";
      setTimeout(() => router.push("/admin"), 1200);
    }
  } catch (err) {
    errorMsg.value = "Network error: " + err.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.edit-box {
  max-width: 550px;
  background-color: #19b39e4a;
  margin-top: 40px;
  margin-left: 45%;
  padding: 28px 32px;
  border-radius: 6px;
}
.edit-box h2 {
  text-align: center;
  margin: 0 0 20px 0;
  font-size: 1.5rem;
}
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
label {
  font-weight: 600;
  margin-top: 4px;
  margin-left: 20%;
  margin-bottom: 2px;
}
.hint {
  font-weight: normal;
  color: #6b7280;
  font-size: 0.85rem;
}
.input {
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  width: 60%;
  background-color: rgba(247, 248, 248, 0.743);
  margin-bottom: 10px;
  margin-left: 20%;
}
.input:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.input:focus {
  border-color: #0ea5a4;
  outline: none;
  box-shadow: 0 0 0 2px rgba(14, 165, 164, 0.2);
}
.form-btn {
  margin-top: 12px;
  width: 40%;
  padding: 10px;
  font-size: 1rem;
  border-radius: 6px;
  background-color: rgb(2, 33, 33);
  color: white;
  font-weight: 700;
  margin-left: 30%;
  border: none;
  cursor: pointer;
}
.form-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.back-link {
  display: block;
  text-align: center;
  margin-top: 18px;
  font-weight: 600;
  color: #0ea5a4;
  text-decoration: none;
  cursor: pointer;
}
.back-link:hover {
  text-decoration: underline;
}
.alert {
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 14px;
  font-weight: 600;
  font-size: 0.9rem;
}
.error   { background: #fde8e8; color: #7f1d1d; border: 1px solid #f5c6c6; }
.success { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
</style>