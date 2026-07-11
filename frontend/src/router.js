import { createRouter, createWebHistory } from "vue-router"
import Login from "./components/Login.vue"
import Register from "./components/Register.vue"
import AdminDashboard from "./components/Admin/Dashboard.vue"
import StaffDashboard from "./components/Staff/Dashboard.vue"
import UserDashboard from "./components/User/Dashboard.vue"

const routes = [
    {
        "path": "/", redirect: "/login"
    },
    {
        "path": "/login", component: Login
    },
    {
        "path": "/register", component: Register
    },
    {
        "path": "/admin/dashboard", component: AdminDashboard
    },
    {
        "path": "/staff/dashboard", component: StaffDashboard
    },
    {
        "path": "/user/dashboard", component: UserDashboard
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
