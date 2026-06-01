import { createRouter,  createWebHistory } from 'vue-router'

const router = createRouter({history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    { 
      path: '/',
      name: 'login',
      component: () => import('../views/auth_views/LoginView.vue') 
    },

    { path:'/login',    
      name: 'login',    
      component: () => import('../views/auth_views/LoginView.vue') 
    },

    { path:'/register', 
      name: 'register', 
      component: () => import('../views/auth_views/RegisterView.vue') 
    },

    { path:'/admin',             
      name: 'admin_dashboard',    
      component: () => import('../views/admin_views/AdminDashView.vue'),        
      meta: { role: 'admin' } 
    },

    { path: '/create-doctor',     
      name: 'create_doctor',      
      component: () => import('../views/admin_views/createdocView.vue'),        
      meta: { role: 'admin' } 
    },

    { path: '/edit-doctor/:id',   
      name: 'edit_doctor',        
      component: () => import('../views/admin_views/EditDoctorView.vue'),       
      meta: { role: 'admin' } 
    },

    {path: '/past-appointments', 
      name: 'past_appointments',  
      component: () =>import('../views/admin_views/PastAppointmentsView.vue'), 
      meta: { role: 'admin' } 
    },

    {path: '/patient-history/:id', 
      name: 'patient_history', 
      component: () =>import('../views/doctor_views/PatientHistoryView.vue'),
       meta: { role: ['admin', 'doctor'] }
       },
    {path: '/edit-patient/:id',    
      name: 'edit_patient',    
      component:() =>import('../views/admin_views/EditPatientView.vue'),   
       meta: { role:['admin', 'patient'] }},

    { path:'/doctor',                       
       name: 'doctor_dashboard',   
       component: () =>import('../views/doctor_views/DoctorDashView.vue'),       
        meta: { role: 'doctor' } 
      },
    {path: '/doctor/availability',           
      name: 'doctor_availability', 
      component: () =>import('../views/doctor_views/DoctorAvailabilityView.vue'), 
      meta: { role: 'doctor' } 
    },


    { path: '/doctor/appointment/:id/update', 
      name: 'update_appointment', 
      component:() => import('../views/doctor_views/UpdateApptView.vue'),         
      meta: { role: 'doctor' }
     },

    {path: '/patient',              
      name:'patient_dashboard',   
      component: () =>import('../views/patient_views/PatientDashView.vue'),     
      meta: { role: 'patient' }
    },

    { path:'/patient/history',      
      name: 'patient_history_own', 
      component: () => import('../views/doctor_views/PatientHistoryView.vue'),  
      meta: { role: 'patient' }
    },

    { path:'/doctors/:id',          
      name: 'department_detail',   
      component:() => import('../views/patient_views/DeptDetailView.vue'),      
      meta: { role: 'patient' } 
    },
    { path:'/doctor-detail/:id',   
       name: 'doctor_detail',       
       component: () => import('../views/patient_views/DoctorDetailView.vue'),    
       meta: { role: 'patient' } 
      },

    { path: '/book-appointment/:id', 
      name: 'book_appointment',    
      component: () => import('../views/patient_views/CheckAvailView.vue'),     
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