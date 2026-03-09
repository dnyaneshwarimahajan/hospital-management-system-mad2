// import { createRouter, createWebHistory } from 'vue-router'
// import HomeView from '../views/HomeView.vue'

// const router = createRouter({
//   history: createWebHistory(import.meta.env.BASE_URL),
//   routes: [
//     {
//       path: '/',
//       name: 'home',
//       component: HomeView,
//     },
//     {
//       path: '/about',
//       name: 'about',
//       // route level code-splitting
//       // this generates a separate chunk (About.[hash].js) for this route
//       // which is lazy-loaded when the route is visited.
//       component: () => import('../views/AboutView.vue'),
//     },
//     {
//       path: '/login',
//       name: 'login',
//       component: () => import('../views/LoginView.vue'),
//     },
//     {
//       path: '/register',
//       name: 'registeration page',
//       component: () => import('../views/RegisterView.vue')
//     },

//     {
//     path: '/doctor',
//     name: 'doctor_dashboard',
//     component: () => import('../views/DoctorDashView.vue'),
//     meta: { role: 'doctor' }
//     },
//     {
//     path: '/doctor/patient/:id/history',
//     name: 'patient_history',
//     component: () => import('../views/PatientHistoryView.vue'),
//     meta: { role: 'doctor' }
//     },
//     {
//       path: '/admin/'
//     }
//    {
//     path: '/doctor/availability',
//     name: 'doctor_availability',
//     component: () => import('../views/DoctorAvailabilityView.vue'),
//     meta: { role: 'doctor' }
//     },

//     {
//       path:'/admin',
//       name: 'admin_dashboard',
//       component: () => import('../views/AdminDashView.vue'),
//       meta: {role: 'admin'}
//     },
//     {
//       path:'/create-doctor',
//       name: 'create doctor page',
//       component: () => import('../views/createdocView.vue'),
//       meta: {role: 'admin'}

//     },
//     {
//       path: '/edit-doctor/:id',
//       name: 'edit_doctor',
//       component: () => import('../views/EditDoctorView.vue'),
//       meta: { role: 'admin' }
//     },
//     {
//       path: '/edit-patient/:id',
//       name: 'edit_patient',
//       component: () => import('../views/EditPatientView.vue'),
//       meta: { role: ['admin', 'patient'] }  // ← array instead of single role
//     },
//     {
//       path: '/patient',
//       name: 'Patient_dashboard',
//       component : () => import('../views/PatientDashView.vue'),
//       meta: {role: 'patient'}
//     },
//     // {
//     //   path:'/patient/departments',
//     //   name: 'department_details',
//     //   component : () => import('../views/DeptDetailView.vue'),
//     //   meta: {role : 'patient'}
//     // },
//     {
//       path: '/doctors/:id',
//       name: 'department_detail',
//       component: () => import('../views/DeptDetailView.vue'),
//       meta: { role: 'patient' }
//     },

//   {
//     path: '/book-appointment/:id',
//     name: 'book_appointment',
//     component: () => import('../views/CheckAvailView.vue'),
//     meta: { role: 'patient' }
//   },
//   {
//     path: '/doctor-detail/:id',
//     name: 'doctor_detail',
//     component: () => import('../views/DoctorDetailView.vue'),
//     meta: { role: 'patient' }
//   },
//   {
//   path: '/doctor/appointment/:id/update',
//   name: 'update_appointment',
//   component: () => import('../views/UpdateApptView.vue'),
//   meta: { role: 'doctor' }
// },
//   ],
// })
// // router.beforeEach((to, from, next)=>{

// //   const role = localStorage.getItem("role")

// //   // Allow login page always
// //   if(to.path === "/login"){
// //     next()
// //     return
// //   }

// //   // Check protected routes
// //   if(to.meta.role){

// //     if(!role){
// //       alert("Please Login First")
// //       next("/login")
// //       return
// //     }

// //     if(to.meta.role !== role){
// //       alert("Unauthorized Access")
// //       next("/login")
// //       return
// //     }
// //   }

// //   next()
// // })

// router.beforeEach((to, from, next) => {
//   const role = localStorage.getItem("role")

//   if (to.path === "/login") {
//     next()
//     return
//   }

//   if (to.meta.role) {
//     if (!role) {
//       alert("Please Login First")
//       next("/login")
//       return
//     }

//     const allowed = Array.isArray(to.meta.role) ? to.meta.role : [to.meta.role]
//     if (!allowed.includes(role)) {
//       alert("Unauthorized Access")
//       next("/login")
//       return
//     }
//   }

//   next()
// })

// export default router


import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    // ── Public ─────────────────────────────────────────────────────────────
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },

    // ── Admin ──────────────────────────────────────────────────────────────
    {
      path: '/admin',
      name: 'admin_dashboard',
      component: () => import('../views/AdminDashView.vue'),
      meta: { role: 'admin' }
    },
    {
      path: '/create-doctor',
      name: 'create_doctor',
      component: () => import('../views/createdocView.vue'),
      meta: { role: 'admin' }
    },
    {
      path: '/edit-doctor/:id',
      name: 'edit_doctor',
      component: () => import('../views/EditDoctorView.vue'),
      meta: { role: 'admin' }
    },
    {
      path: '/past-appointments',
      name: 'past_appointments',
      component: () => import('../views/PastAppointmentsView.vue'),
      meta: { role: 'admin' }
    },

    // ── Shared: Admin + Doctor ─────────────────────────────────────────────
    {
      path: '/patient-history/:id',
      name: 'patient_history',
      component: () => import('../views/PatientHistoryView.vue'),
      meta: { role: ['admin', 'doctor'] }
    },
    {
      path: '/edit-patient/:id',
      name: 'edit_patient',
      component: () => import('../views/EditPatientView.vue'),
      meta: { role: ['admin', 'patient'] }
    },

    // ── Doctor ─────────────────────────────────────────────────────────────
    {
      path: '/doctor',
      name: 'doctor_dashboard',
      component: () => import('../views/DoctorDashView.vue'),
      meta: { role: 'doctor' }
    },
    {
      path: '/doctor/availability',
      name: 'doctor_availability',
      component: () => import('../views/DoctorAvailabilityView.vue'),
      meta: { role: 'doctor' }
    },
    {
      path: '/doctor/appointment/:id/update',
      name: 'update_appointment',
      component: () => import('../views/UpdateApptView.vue'),
      meta: { role: 'doctor' }
    },

    // ── Patient ────────────────────────────────────────────────────────────
    {
      path: '/patient',
      name: 'patient_dashboard',
      component: () => import('../views/PatientDashView.vue'),
      meta: { role: 'patient' }
    },
    {
      path: '/patient/history',
      name: 'patient_history_own',
      component: () => import('../views/PatientHistoryView.vue'),
      meta: { role: 'patient' }
    },
    {
      path: '/doctors/:id',
      name: 'department_detail',
      component: () => import('../views/DeptDetailView.vue'),
      meta: { role: 'patient' }
    },
    {
      path: '/doctor-detail/:id',
      name: 'doctor_detail',
      component: () => import('../views/DoctorDetailView.vue'),
      meta: { role: 'patient' }
    },
    {
      path: '/book-appointment/:id',
      name: 'book_appointment',
      component: () => import('../views/CheckAvailView.vue'),
      meta: { role: 'patient' }
    },

  ],
})

router.beforeEach((to, from, next) => {
  const role = localStorage.getItem("role")

  if (to.path === "/login" || to.path === "/register" || to.path === "/") {
    next()
    return
  }

  if (to.meta.role) {
    if (!role) {
      alert("Please Login First")
      next("/login")
      return
    }

    const allowed = Array.isArray(to.meta.role) ? to.meta.role : [to.meta.role]
    if (!allowed.includes(role)) {
      alert("Unauthorized Access")
      next("/login")
      return
    }
  }

  next()
})

export default router

