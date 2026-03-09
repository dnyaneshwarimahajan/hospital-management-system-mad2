<template>
  <div class="form-container">
    <h2 class="form-title">Create New Doctor</h2>

    <div v-if="errorMsg" class="alert error">{{ errorMsg }}</div>
    <div v-if="successMsg" class="alert success">{{ successMsg }}</div>

    <form @submit.prevent="createDoctor">
      <div class="input-group">
        <label>Doctor Name</label>
        <input class="input" type="text" v-model="username" required />
      </div>

      <div class="input-group">
        <label>Email</label>
        <input class="input" type="email" v-model="email" required />
      </div>

      <div class="input-group">
        <label>Password</label>
        <input class="input" type="password" v-model="password" required />
      </div>

      <div class="input-group">
        <label>Select Existing Department</label>
        <!-- FIX 3: Dynamic departments fetched from backend -->
        <select class="input" v-model="departmentId" :disabled="!!newDepartmentName">
          <option value="">-- Select existing department --</option>
          <option v-for="dept in departments" :key="dept.id" :value="dept.id">
            {{ dept.dept_name }}
          </option>
        </select>
        <small v-if="loadingDepts">Loading departments...</small>
      </div>

      <div class="divider">OR create a new department</div>

      <div class="input-group">
        <label>New Department Name</label>
        <input
          class="input"
          type="text"
          v-model="newDepartmentName"
          :disabled="!!departmentId"
          placeholder="Leave blank if selecting existing"
        />
      </div>

      <div class="input-group">
        <label>New Department Description</label>
        <textarea
          class="input"
          v-model="newDepartmentDescription"
          :disabled="!!departmentId"
          placeholder="Leave blank if selecting existing"
        ></textarea>
      </div>

      <div class="btn-row">
        <button class="btn create" type="submit" :disabled="loading">
          {{ loading ? 'Creating...' : 'Create Doctor' }}
        </button>
        <RouterLink class="btn btn-secondary" to="/admin">Cancel</RouterLink>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const username = ref("");
const email = ref("");
const password = ref("");
const departmentId = ref("");
const newDepartmentName = ref("");
const newDepartmentDescription = ref("");

const departments = ref([]);
const loadingDepts = ref(false);
const loading = ref(false);
const errorMsg = ref("");
const successMsg = ref("");

// ✅ FIX 2: Correct header name — "Authentication-Token" not "Authentication"
function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

// ✅ FIX 3: Fetch real departments from backend on mount
async function fetchDepartments() {
  loadingDepts.value = true;
  try {
    const res = await fetch("http://127.0.0.1:5000/api/admin/departments", {
      headers: authHeaders(),
    });
    const data = await res.json();
    departments.value = data.departments || [];
  } catch (err) {
    console.error("Failed to load departments:", err);
  } finally {
    loadingDepts.value = false;
  }
}

onMounted(fetchDepartments);

async function createDoctor() {
  errorMsg.value = "";
  successMsg.value = "";

  // Must pick one: existing dept OR new dept name
  if (!departmentId.value && !newDepartmentName.value) {
    errorMsg.value = "Please select an existing department or enter a new department name.";
    return;
  }

  loading.value = true;

  const payload = {
    username: username.value,
    email: email.value,
    password: password.value,
    department_id: departmentId.value || null,
    new_department_name: newDepartmentName.value || null,
    new_department_description: newDepartmentDescription.value || null,
  };

  try {
    // ✅ FIX 1: Correct URL — /api/admin/create-doctor not /api/admin/doctor
    const res = await fetch("http://127.0.0.1:5000/api/admin/create-doctor", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      errorMsg.value = data.message || `Error ${res.status}`;
    } else {
      successMsg.value = "Doctor created successfully! Redirecting...";
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
.form-container {
  max-width: 560px;
  margin: 40px auto;
  background-color: #19b39e4a;
  padding: 28px 32px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.form-title {
  margin-bottom: 20px;
  text-align: center;
  color: #052c2f;
}

.input-group {
  margin-bottom: 16px;
}

label {
  font-weight: 600;
  margin-bottom: 5px;
  display: block;
  color: #054145;
}

.input,
select,
textarea {
  width: 100%;
  padding: 9px 11px;
  border-radius: 6px;
  border: 1px solid #cdd;
  font-size: 0.95rem;
  background: #ffffffcc;
}

textarea {
  resize: vertical;
  min-height: 70px;
}

.input:disabled,
select:disabled,
textarea:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.divider {
  text-align: center;
  color: #6b7280;
  font-size: 0.85rem;
  margin: 8px 0 16px;
  position: relative;
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 38%;
  height: 1px;
  background: #ccc;
}

.divider::before { left: 0; }
.divider::after  { right: 0; }

.btn-row {
  display: flex;
  gap: 12px;
  margin-top: 22px;
}

.btn {
  flex: 1;
  padding: 10px;
  color: #fff;
  cursor: pointer;
  border-radius: 6px;
  border: none;
  font-weight: 700;
  font-size: 0.95rem;
  text-align: center;
  text-decoration: none;
}

.create {
  background-color: rgb(2, 33, 33);
}

.create:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #360202da;
  display: flex;
  align-items: center;
  justify-content: center;
}

.alert {
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 0.9rem;
}

.error   { background: #fde8e8; color: #7f1d1d; border: 1px solid #f5c6c6; }
.success { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }

small {
  color: #6b7280;
  font-size: 0.8rem;
  margin-top: 3px;
  display: block;
}
</style>