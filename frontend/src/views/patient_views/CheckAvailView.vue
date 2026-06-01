<template>
  <div class="container">
    <h2>Dr.{{ doctor.name }} {{ rescheduleId ? 'Reschedule Appointment' : 'Book Appointment' }}</h2>
    <p class="lead">Select a slot</p>

    <div v-if="flashMsg" class="flash" :class="flashClass">{{ flashMsg }}</div>

    <div v-if="patientHasBooking" class="note">
      You already have one active booking. You cannot book another slot.
    </div>

    <div class="row" v-for="r in grid" :key="r.date">
      <div class="date-box">{{ r.date }}</div>

      <div class="slots">

        <button
          v-if="isBooked(r.date, 'slot1')"
          class="slot-btn slot-booked"
          disabled
        >{{ slotLabels.slot1 }} Booked</button>

        <button
          v-else-if="!r.slot_1"
          class="slot-btn slot-unavailable"
          disabled
        >{{ slotLabels.slot1 }}Unavailable</button>

        <button
          v-else-if="patientHasBooking"
          class="slot-btn slot-unavailable"
          disabled
        >{{ slotLabels.slot1 }} Book</button>

        <button
          v-else
          class="slot-btn slot-available"
          @click="bookSlot(r.date, 'slot1')"
        >{{ slotLabels.slot1 }} Book</button>

        <button
          v-if="isBooked(r.date, 'slot2')"
          class="slot-btn slot-booked"
          disabled
        >{{ slotLabels.slot2 }}Booked</button>

        <button
          v-else-if="!r.slot_2"
          class="slot-btn slot-unavailable"
          disabled
        >{{ slotLabels.slot2 }}Unavailable</button>

        <button
          v-else-if="patientHasBooking"
          class="slot-btn slot-unavailable"
          disabled
        >{{ slotLabels.slot2 }} Book</button>

        <button
          v-else
          class="slot-btn slot-available"
          @click="bookSlot(r.date, 'slot2')"
        >{{ slotLabels.slot2 }} Book</button>

      </div>
    </div>

    <div style="margin-top:12px;">
      <a class="back-link" @click="$router.push('/patient')">Back</a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const BASE = "https://hms-backend-cvcn.onrender.com";

const doctorId = route.params.id;
const rescheduleId = route.query.reschedule || null;
const doctor = ref({ name: "" });
const grid = ref([]);
const bookedSlots = ref([]); 
const patientHasBooking = ref(false);
const flashMsg = ref("");
const flashClass = ref("");

const slotLabels = {
  slot1: "8:00 AM – 12:00 PM",
  slot2: "4:00 PM – 9:00 PM"
};

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authentication-Token": localStorage.getItem("token"),
  };
}

function isBooked(date, slot) {
  return bookedSlots.value.some(b => b.date === date && b.slot === slot);
}

async function fetchAvailability() {
  try {
    const res = await fetch(`${BASE}/api/patient/doctor/${doctorId}/availability`, {
      headers: authHeaders(),
    });
    const data = await res.json();

    const dateMap = {};
    (data.available_slots || []).forEach(s => {
      if (!dateMap[s.date]) dateMap[s.date] = { date: s.date, slot_1: false, slot_2: false };
      if (s.slot === "slot1") dateMap[s.date].slot_1 = true;
      if (s.slot === "slot2") dateMap[s.date].slot_2 = true;
    });
    grid.value = Object.values(dateMap);

    bookedSlots.value = data.booked_slots || [];
  } catch (err) {
    console.error("Failed to load availability:", err);
  }
}

async function fetchDoctorInfo() {
  try {
    const res = await fetch(`${BASE}/api/patient/doctors/search?q=`, {
      headers: authHeaders(),
    });
    const data = await res.json();
    const found = (data.doctors || []).find(d => d.id == doctorId);
    if (found) doctor.value = found;
  } catch (err) {
    console.error("Failed to load doctor info:", err);
  }
}



async function checkExistingBooking() {
  try {
    const res = await fetch(`${BASE}/api/patient/dashboard?t=${Date.now()}`, {
      headers: authHeaders(),
    });
    const data = await res.json();
    const upcoming = data.upcoming_appointments || [];

    if (rescheduleId) {
      patientHasBooking.value = upcoming.filter(
        a => a.id !== parseInt(rescheduleId)
      ).length > 0;
    } else {
      patientHasBooking.value = upcoming.length > 0;
    }
  } catch (err) {
    console.error("Failed to check existing bookings:", err);
  }
}

async function bookSlot(date, slot) {
  try {
    let res;
    if (rescheduleId) {
      res = await fetch(`${BASE}/api/patient/appointment/${rescheduleId}/reschedule`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify({ date, slot })
      });
    } else {
      res = await fetch(`${BASE}/api/patient/appointment/book`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ doctor_id: parseInt(doctorId), date, slot })
      });
    }

    const data = await res.json();
    if (res.ok) {
      flashMsg.value = rescheduleId ? "Appointment rescheduled!" : "Appointment booked!";
      flashClass.value = "success";
      patientHasBooking.value = true;
      bookedSlots.value.push({ date, slot });
    } else {
      flashMsg.value = data.message || "Failed.";
      flashClass.value = "danger";
    }
  } catch (err) {
    flashMsg.value = "Network error: " + err.message;
    flashClass.value = "danger";
  }
}

onMounted(() => {
  fetchDoctorInfo();
  fetchAvailability();
  checkExistingBooking();
});
</script>

<style scoped>
.container {
  max-width: 750px;
  margin: 20px auto;
  padding: 12px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  background: #fff;
}

h2 
{ margin: 0 0 6px; 
  font-size: 1.2rem;
 }
p.lead 
{ margin: 0 0 12px; 
  color: #555;
 }

.flash 
{ padding: 10px;
   border-radius: 6px;
    margin-bottom: 8px;
     font-weight: 500;
      border: 1px solid #ddd;
       background: #fafafa; 
       color:#111; }
.flash.success 
{ border-color:#cfeadf; 
  background:#f7fff7; }
.flash.warning { border-color:#f3e2c7; background:#fffaf2; }
.flash.danger 
 { border-color:#f4d7d7;
   background:#fff6f6; }

.row { 
  display:flex;
   gap:12px; 
   align-items:center; 
   margin:10px 0; 
   flex-wrap:wrap; }

.date-box {
  min-width:120px;
  padding:8px;
  border-radius:6px;
  text-align:center;
  font-weight:600;
  border:1px solid #eee;
  background:#fafafa;
}

.slots { display:flex;
   gap:8px; 
   flex-wrap:wrap; 
   align-items:center; }

.slot-btn {
  padding:8px 10px;
  border-radius:6px;
  border:1px solid #bbb;
  background:transparent;
  cursor:pointer;
  font-weight:600;
  font-size:0.95rem;
}

.slot-unavailable 
{ background:#eee;
   color:#777; 
   cursor:not-allowed; }
.slot-booked      
{ background:#f55656; 
  color:#fff; 
  cursor:not-allowed; }
.slot-available   

{ border-color:#2d8f6f; 
  color:#0b5132; }
.slot-available:hover {
   background:#f0fff8; }

.note {
  margin:8px 0;
  padding:8px;
  border-radius:6px;
  border:1px solid #f0d9a8;
  background:#fffaf0;
}

.back-link {
  display: block;
  text-align: center;
  margin-top: 18px;
  font-weight: 600;
  color: rgba(2, 43, 35, 0.814);
  text-decoration: none;
  cursor: pointer;
}

.back-link:hover { text-decoration: underline; }
</style>