import { createRouter, createWebHistory } from "vue-router"

import Login from "./components/Login.vue"
import Register from "./components/Register.vue"

import AdminDashboard from "./components/Admin/Dashboard.vue"
import AdminManageTreks from "./components/Admin/ManageTreks.vue"
import AdminManageStaff from "./components/Admin/ManageStaff.vue"
import AdminManageUsers from "./components/Admin/ManageUsers.vue"
import AdminSearch from "./components/Admin/Search.vue"

import StaffDashboard from "./components/Staff/Dashboard.vue"
import StaffManageTrek from "./components/Staff/ManageTrek.vue"
import UserDashboard from "./components/User/Dashboard.vue"

const routes = [
    {
        path: "/",
        redirect: "/login"
    },
    {
        path: "/login",
        component: Login
    },
    {
        path: "/register",
        component: Register
    },

    // Admin — Milestone 3
    {
        path: "/admin/dashboard",
        component: AdminDashboard
    },
    {
        path: "/admin/treks",
        component: AdminManageTreks
    },
    {
        path: "/admin/staff",
        component: AdminManageStaff
    },
    {
        path: "/admin/users",
        component: AdminManageUsers
    },
    {
        path: "/admin/search",
        component: AdminSearch
    },

    // Staff — Milestone 4
    {
        path: "/staff/dashboard",
        component: StaffDashboard
    },
    {
        path: "/staff/treks/:trek_id",
        component: StaffManageTrek
    },

    // Trekker — existing Milestone 2 dashboard
    {
        path: "/user/dashboard",
        component: UserDashboard
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
