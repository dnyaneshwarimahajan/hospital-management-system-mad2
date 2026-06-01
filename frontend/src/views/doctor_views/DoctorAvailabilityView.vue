<template>
  <div class="form">
    <h3>Set Availability Dr. {{ doctorName }}</h3>

    <div v-for="r in grid" :key="r.date" style="display:flex;gap:12px;align-items:center;margin:6px 0;">
      <div style="width:140px;background:#eaf4ff;padding:8px;border-radius:4px;"> {{ r.date }} </div>

      <div class="slot" :class="{ active: r.slot1 }" @click="toggleSlot(r, 'slot1')"> 08:00 - 12:00 </div>
      <div class="slot":class="{ active: r.slot2 }"@click="toggleSlot(r, 'slot2')"> 04:00 - 09:00 </div>
    </div>

    <div style="margin-top:12px;">
      <button @click="saveAvailability">Save</button>
      <RouterLink to="/doctor" class="back-link">Back</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const BASE = "https://hms-backend-cvcn.onrender.com";

const doctorName = ref(localStorage.getItem("name") || "");
const grid = ref([]);

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

function buildGrid(existingAvailability = []) {
  const days = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date();
    d.setDate(d.getDate() + i);
    const dateStr = d.toISOString().split("T")[0];

    const existing = existingAvailability.find(a => a.date === dateStr);
    days.push({
      date: dateStr,
      slot1: existing ? existing.slot_1 : false,
      slot2: existing ? existing.slot_2 : false,
    });
  }
  grid.value = days;
}

async function fetchAvailability() {
  try {
    const res = await fetch(`${BASE}/api/doctor/dashboard`, {
      headers: authHeaders(),
    });
    const data = await res.json();
    buildGrid(data.availability || []);
  } catch (err) {
    console.error("Failed to load availability:", err);
    buildGrid();
  }
}

function toggleSlot(row, slot) {
  row[slot] = !row[slot];
}

async function saveAvailability() {
  const payload = grid.value.map(r => ({
    date: r.date,
    slot_1: r.slot1,
    slot_2: r.slot2,
  }));

  try {
    await fetch(`${BASE}/api/doctor/availability`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ availability: payload }),
    });
    alert("Availability saved!");
    router.push("/doctor");
  } catch (err) {
    console.error("Failed to save availability:", err);
  }
}

onMounted(fetchAvailability);
</script>

<style scoped>
.form {
  max-width: 750px;
  margin: 20px auto;
  font-family: Arial, sans-serif;
  padding: 12px;
  background: #fbfbfbc7;
}

.slot {
  padding: 8px;
  border: 2px solid #ccc;
  border-radius: 6px;
  cursor: pointer;
}

.slot.active {
  border-color: green;
}

.back-link {
  display: block;
  text-align: center;
  margin-top: 18px;
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
  cursor: pointer;
}

button {
  width: 50%;
  border-radius: 5%;
  margin-left: 25%;
  margin-top: 14px;
  background-color: #3b95e38a;
  border: 1px solid #ccc;
  padding: 6px;
  cursor: pointer;
}
</style>