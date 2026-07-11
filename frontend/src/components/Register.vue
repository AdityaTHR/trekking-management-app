<template>
    <div class="d-flex justify-content-center mt-5">
        <div class="card" style="width: 20rem;">
            <div class="card-body">
                <h5 class="card-title text-center mb-1">Create User Account</h5>
                <p class="text-center text-muted mb-3" style="font-size: 0.85rem;">Register as a Trekker</p>

                <div v-if="message" class="alert alert-danger mt-2 mb-2" role="alert">
                    {{ message }}
                </div>

                <div class="form-floating mb-3">
                    <input type="text" class="form-control" v-model="formdata.name" id="floatingName"
                        placeholder="Full Name">
                    <label for="floatingName">Full Name</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="email" class="form-control" v-model="formdata.email" id="floatingInput"
                        placeholder="name@example.com">
                    <label for="floatingInput">Email address</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="password" class="form-control" v-model="formdata.password" id="floatingPassword"
                        placeholder="Password">
                    <label for="floatingPassword">Password</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="password" class="form-control" v-model="formdata.confirm_password"
                        id="floatingConfirm" placeholder="Confirm Password">
                    <label for="floatingConfirm">Confirm Password</label>
                </div>
                <div class="form-floating">
                    <input type="tel" class="form-control" v-model="formdata.contact_number" id="floatingContact"
                        placeholder="Contact Number">
                    <label for="floatingContact">Contact Number</label>
                </div>

                <!--
                  NOTE: unlike the reference app's Register.vue, there is
                  deliberately NO role <select> here. Only Trekkers can
                  self-register — the backend forces role="trekker"
                  regardless of what's sent, so a role picker here would be
                  misleading. Staff accounts are created by Admin only.
                -->

                <div class="d-flex justify-content-center mt-3">
                    <button class="btn btn-primary" @click="register">Register</button>
                </div>
                <p class="text-center mt-3 mb-0">
                    Already have an account? <router-link to="/login">Login here</router-link>
                </p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "RegisterComp",
    data() {
        return {
            formdata: {
                name: "",
                email: "",
                password: "",
                confirm_password: "",
                contact_number: "",
            },
            message: null
        }
    },
    methods: {
        async register() {
            try {
                const response = await fetch("http://localhost:5000/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(this.formdata)
                })
                const data = await response.json()
                if (response.status == 200) {
                    this.$router.push("/login")
                }
                else if (response.status == 409) {
                    this.message = data.message
                }
                else if (response.status == 400) {
                    this.message = data.message
                }
            }
            catch (error) {
                console.log(error.message)
            }
        }
    }
}
</script>
