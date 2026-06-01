<template>
  <header>
    <div class="nav-inner">

      <div class="brand">
        Hospital Management
      </div>

      <nav>
        <ul>
          <template v-if="!userName">
            <li><RouterLink to="/login">Login</RouterLink></li>
            <li><RouterLink to="/register">Register</RouterLink></li>
          </template>

          <template v-if="role === 'admin'">
            <li>
              <input
                type="search"
                placeholder="Search..."
                v-model="searchQuery"
                @input="handleSearch"
              />
            </li>
          </template>

          <template v-if="role === 'patient'">
            <li><RouterLink to="/patient/history">History</RouterLink></li>
            <li><RouterLink :to="`/edit-patient/${userId}`">Edit Profile</RouterLink></li>
          </template>

          <li v-if="userName">
            <a @click="logout">Logout</a>
          </li>
        </ul>
      </nav>

    </div>
  </header>

  <div class="container">
    <router-view />
  </div>
</template>

<script>
import { RouterLink } from "vue-router";

export default {
  components: { RouterLink },

  data() {
    return {
      userName: localStorage.getItem("name"),
      role: localStorage.getItem("role"),
      userId: localStorage.getItem("id"),
      searchQuery: ""
    };
  },

  methods: {
    logout() {
      localStorage.clear();
      this.userName = null;
      this.role = null;
      this.$router.push("/login");
    },
    handleSearch() {
      if (this.role === 'admin') {
        this.$router.push({ path: '/admin', query: { q: this.searchQuery } });
      }
    }
  },

  watch: {
    $route() {
      this.userName = localStorage.getItem("name");
      this.role = localStorage.getItem("role");
      this.userId = localStorage.getItem("id");
    }
  }
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, Helvetica, sans-serif;
  background-image: url('/image.png');
  color: #222;
}

header {
  background: linear-gradient(180deg, #082ba9a6, #19b39eb9);
  padding: 15px 0;
  color: #fff;
}

.nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand .title {
  font-size: 1.2rem;
  font-weight: bold;
}

nav ul {
  list-style: none;
  display: flex;

  align-items: center;
  gap: 14px;
}

nav a {
  color: #fff;


  text-decoration: none;
  padding: 6px 10px;
  font-size: 0.95rem;
  border-radius: 4px;
}

nav a:hover {

  background: #3a3a3a49;
}

.nav-search input {
  padding: 6px 10px;
  border: 1px solid #ccc;

  border-radius: 4px;
  outline: none;
  font-size: 0.9rem;
}

.container {
  max-width: 1100px;
  padding: 0px;
  border-radius: 6px;

  box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
}

.flash {
  padding: 10px;
  margin-bottom: 12px;
  border-radius: 4px;
  width: 80%;
  font-size: 0.9rem;
}

.flash.success 
{ background: #e7f9ef; 
  border-left: 4px solid #22c55e;
 }
.flash.warning 
{ background: #fff8dd; 
  border-left: 4px solid #eab308; 
}
.flash.danger  
{ background:#fde7e7;
 border-left: 4px solid #ef4444; 
 }
</style>