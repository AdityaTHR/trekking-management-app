<template>
    <div class="form-floating mb-3">
      <input type="email" class="form-control" v-model="formdata.email" id="floatingInput" placeholder="name@example.com">
      <label for="floatingInput">Email address</label>
    </div>
    <div class="form-floating">
      <input type="password" class="form-control" v-model="formdata.password" id="floatingPassword" placeholder="Password">
      <label for="floatingPassword">Password</label>
    </div>
    <button class="btn btn-primary" @click="login" >Login</button>
</template>

<script>
  export default {
    name: "Login-Component",
    data() {
      return {
        formdata: {
          email: '',
          password: ''
        }
      }
    },
    methods: {
      login() {
        console.log('Email:', this.formdata.email);
        console.log('Password:', this.formdata.password);
      }
    }
  }
</script>