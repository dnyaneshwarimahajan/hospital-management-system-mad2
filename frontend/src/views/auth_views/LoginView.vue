<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const password = ref('');
const passwordError = ref('');
const errorMsg = ref('');
const id = ref('');
const loading = ref(false);

async function login() {
    errorMsg.value = '';

    if (username.value === '' || password.value === '') {
        errorMsg.value = 'Please fill in all fields';
        return;
    }

    loading.value = true;

    try {
        const response = await fetch("import.meta.env.VITE_API_BASE_URL/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: username.value,
                password: password.value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            errorMsg.value = data.message || 'Login failed';
            return;
        }

        const token = data.auth_token;
        const role  = data.roles[0];
        const name  = data.username;
        const id    = data.id; 

        if (!token) {
            errorMsg.value = 'Token generate nhi zhalay';
            return;
        }

        localStorage.setItem('token', token);
        localStorage.setItem('role', role);
        localStorage.setItem('name', name);
        localStorage.setItem('id', id);

        if (role === 'admin')        router.push('/admin');
        else if (role === 'doctor')  router.push('/doctor');
        else                         router.push('/patient');

    } catch (err) {
        errorMsg.value = 'Network error: ' + err.message;
    } finally {
        loading.value = false;
    }
}
</script>

<template>
  <div class="login">
    <h2>Login</h2>

    <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

    <form @submit.prevent="login">

      <label>Username</label>
      <input type="text" class="input" placeholder="Enter username" v-model="username"/>
      <label>Password</label>
      <input type="password" class="input" placeholder="Enter password" v-model="password"/>
      <button type="submit" class="btn">Login</button>

    </form>

    <div class="register">
        Don't have an account? <RouterLink to="/register">Register</RouterLink>
    </div>
  </div>

</template>

<style scoped>
.login {
    
    max-width: 380px;
    margin: 100px auto 0;
    background-color: #19b39e4a;
    padding: 26px;
    border-radius: 8px;
}
.login h2 {

    margin: 0 0 14px;
    text-align: center;
}
label {
    display: block;
    text-align: center;
    margin-left: 10%;
    font-weight: 600;
}
.input, .btn {

    width: 80%;
    padding: 10px;
    margin: 6px 0 16px 0;
    margin-left: 10%;
    border-radius: 6px;
    border: 1px solid #d1d5db;
    font-size: 0.95rem;
    background-color: rgba(247, 248, 248, 0.743);
    display: block;
}
.btn {
    width: 50%;
    margin-left: 25%;
    margin-top: 14px;
    background-color: #3b95e38a;
    cursor: pointer;
    font-weight: 600;
}
.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}
.form-text {
    color: #dc2626;
    font-size: 0.8rem;
    margin-left: 10%;
    margin-top: -10px;
    margin-bottom: 8px;
}
.error-msg {
    background: #fde8e8;
    color: #7f1d1d;
    border: 1px solid #f5c6c6;
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 14px;
    font-size: 0.9rem;
    font-weight: 600;
}
.register {
    text-align: center;
    margin-top: 12px;
    font-size: 0.9rem;
}
.register a {
    color: rgba(0,0,0,0.795);
}
</style>