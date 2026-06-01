<template>
  <div class="edit-box">
    <h2>Edit Patient</h2>

    <div v-if="errorMsg" class="alert error">{{ errorMsg }}</div>
    <div v-if="successMsg" class="alert success">{{ successMsg }}</div>

    <form class="edit-form" @submit.prevent="saveChanges">

      <label>Username</label>
      <input type="text" class="input" v-model="form.username" required />

      <label>Email</label>
      <input type="email" class="input" v-model="form.email" required />

      <label>Contact No</label>
      <input type="text" class="input" v-model="form.contact_no" />

      <label>Password <span class="hint">(leave blank to keep same)</span></label>
      <input type="password" class="input" v-model="form.password" placeholder="Enter new password" />

      <button type="submit" class="form-btn" :disabled="loading">
        {{ loading ? 'Saving' : 'Save Changes' }}
      </button>

    </form>
    <a class="back-link" @click.prevent="goBack">Back to Dashboard</a>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

const BASE   = "https://hms-backend-cvcn.onrender.com";
const router = useRouter();
const route  = useRoute();
const id     = route.params.id;

const form = ref({
  username:"",
  email: "",
  contact_no: "",
  password: "",
});

const loading = ref(false);
const errorMsg = ref("");
const successMsg = ref("");

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

function goBack() {
  const role = localStorage.getItem("role");
  if (role === "admin") router.push("/admin");
  else if (role === "patient") router.push("/patient");
  else  router.push("/");
}

async function fetchPatient() {
  try {
    const res  = await fetch(`${BASE}/api/admin/edit-patient/${id}`, {
      headers: authHeaders()
    });
    const data = await res.json();

    if (!res.ok) {
      errorMsg.value = data.message || "Failed to load patient data.";
      return;
    }

    form.value.username = data.username || "";
    form.value.email = data.email || "";
    form.value.contact_no = data.contact_no || "";
  } catch (err) {
    errorMsg.value = "Network error:" + err.message;
  }
}

onMounted(fetchPatient);

async function saveChanges() {
  errorMsg.value = "";
  successMsg.value = "";
  loading.value = true;

  const payload = {
    username: form.value.username || undefined,
    email: form.value.email || undefined,
    contact_no: form.value.contact_no || undefined,
    password: form.value.password || undefined,
  };

  try {
    const res  = await fetch(`${BASE}/api/admin/edit-patient/${id}`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      errorMsg.value = data.message || `Error ${res.status}`;
    } else {
      successMsg.value = "Patient updated successfully! Redirecting";
      setTimeout(() => goBack(), 1200);
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
  margin-left: 30%;
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