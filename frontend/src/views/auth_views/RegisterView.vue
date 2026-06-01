<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const username = ref('');
const email = ref('');
const password = ref('');

const checkUsernameMessage = ref('');
const checkEmailMessage = ref('');
const passwordMessage = ref('');

const emailAvailable = ref(false);
const usernameAvailable = ref(false);

function validatePassword() {
    if (password.value.length < 8)
    {
        passwordMessage.value = 'Password must be at least 8 characters long'
        return false;
    }
    passwordMessage.value = 'valid password';
    return true;
}

function checkEmailAvailibility() {

    fetch('import.meta.env.VITE_API_BASE_URL/api/check-email',
    {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: email.value })
    })
    .then(res => res.json())
    .then(data => {
        if(data.available)
        {
            checkEmailMessage.value = 'Email available'
            emailAvailable.value = true
        }
        else
        {
            checkEmailMessage.value = 'Email already taken'
            emailAvailable.value = false
        }
    })
}

function checkUsernameAvailibility() {

    fetch('import.meta.env.VITE_API_BASE_URL/api/check-username',{
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username: username.value })
    })
    .then(res => res.json())
    .then(data => {
        if(data.available)
        {
            checkUsernameMessage.value = 'Username available'
            usernameAvailable.value = true
        }
        else
        {
            checkUsernameMessage.value = 'Username taken'
            usernameAvailable.value = false
        }
    })
}

async function register(){

    if (!validatePassword()) return; 

    if(!usernameAvailable.value){
        alert('Username already taken');
        return;
    }
    const user = {
        username: username.value,
        email: email.value,
        password: password.value
    }

    const response = await fetch('import.meta.env.VITE_API_BASE_URL/api/register',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(user)
    })

    const data = await response.json()

    if(!response.ok){
        alert(data.message)
    }else{
        alert(data.message)
        router.push('/login')
    }
}
</script>



<template>
    <div class="container-fluid">
        <div class="row justify-content-center mt-3">
            <div class="col-6  align-items-center">
                <h1>Register</h1>
                <form @submit.prevent="register">
                    <div class="mb-3">
                        <label for="exampleInputUsername1" class="form-label">Username</label>
                        <input type="text" class="form-control" id="exampleInputUsername1" @input="checkUsernameAvailibility" v-model="username">
                        <p class="form-text" v-if="checkUsernameMessage">{{ checkUsernameMessage }}</p>
                    </div>
                    <div class="mb-3">
                        <label for="exampleInputEmail1" class="form-label">Email address</label>
                        <input type="email" class="form-control" id="exampleInputEmail1" aria-describedby="emailHelp" @input="checkEmailAvailibility" v-model="email">
                        <p class="form-text" v-if="checkEmailMessage">{{ checkEmailMessage }}</p>
                    </div>
                    <div class="mb-3">
                        <label for="exampleInputPassword1" class="form-label">Password</label>
                        <input type="password" class="form-control" id="exampleInputPassword1" v-model="password" @input="validatePassword">
                        <p class="form-text" v-if="passwordMessage">{{ passwordMessage }}</p>
                    </div>
                    <button type="submit" class="btn btn-primary">Submit</button>
                </form>
            </div>
        </div>
    </div>
</template>