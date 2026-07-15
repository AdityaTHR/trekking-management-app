import { createRouter, createWebHistory } from "vue-router"
import Login from "./components/Login.vue"
import Register from "./components/Register.vue"
import PublicLanding from "./components/PublicLanding.vue"

import AdminDashboard from "./components/Admin/Dashboard.vue"
import AdminManageTreks from "./components/Admin/ManageTreks.vue"
import AdminManageStaff from "./components/Admin/ManageStaff.vue"
import AdminManageUsers from "./components/Admin/ManageUsers.vue"
import AdminSearch from "./components/Admin/Search.vue"
import AdminBookings from "./components/Admin/Bookings.vue"

import StaffDashboard from "./components/Staff/Dashboard.vue"
import StaffManageTrek from "./components/Staff/ManageTrek.vue"

import UserDashboard from "./components/User/Dashboard.vue"
import UserBrowseTreks from "./components/User/BrowseTreks.vue"
import UserHistory from "./components/User/History.vue"
import UserProfile from "./components/User/Profile.vue"

// Each route's `meta.role` lists which role(s) may access it. Routes with no
// `meta.role` (landing, login, register) are public. This is the single
// source of truth the global guard below reads from — individual components
// no longer need to duplicate this "am I allowed here" logic themselves.
const routes = [
    {
        "path": "/", component: PublicLanding
    },
    {
        "path": "/login", component: Login
    },
    {
        "path": "/register", component: Register
    },

    // Admin (Milestone 3)
    {
        "path": "/admin/dashboard", component: AdminDashboard, meta: { role: "admin" }
    },
    {
        "path": "/admin/treks", component: AdminManageTreks, meta: { role: "admin" }
    },
    {
        "path": "/admin/staff", component: AdminManageStaff, meta: { role: "admin" }
    },
    {
        "path": "/admin/users", component: AdminManageUsers, meta: { role: "admin" }
    },
    {
        "path": "/admin/search", component: AdminSearch, meta: { role: "admin" }
    },
    {
        "path": "/admin/bookings", component: AdminBookings, meta: { role: "admin" }
    },

    // Staff (Milestone 4)
    {
        "path": "/staff/dashboard", component: StaffDashboard, meta: { role: "staff" }
    },
    {
        "path": "/staff/treks/:trek_id", component: StaffManageTrek, meta: { role: "staff" }
    },

    // User / Trekker (Milestone 5 & 6)
    {
        "path": "/user/dashboard", component: UserDashboard, meta: { role: "trekker" }
    },
    {
        "path": "/user/treks", component: UserBrowseTreks, meta: { role: "trekker" }
    },
    {
        "path": "/user/history", component: UserHistory, meta: { role: "trekker" }
    },
    {
        "path": "/user/profile", component: UserProfile, meta: { role: "trekker" }
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

function dashboardPathFor(role) {
    if (role === "admin") return "/admin/dashboard"
    if (role === "staff") return "/staff/dashboard"
    if (role === "trekker") return "/user/dashboard"
    return "/login"
}

// ---------------------------------------------------------------------------
// Global navigation guard — replaces the old pattern of every single
// component checking `if (response.status == 401 ...) this.$router.push
// ("/login")` inside its own fetch calls. That still works as a second line
// of defense (a token can expire mid-visit), but route access itself is now
// decided in exactly one place.
// ---------------------------------------------------------------------------
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem("token")
    const role = localStorage.getItem("role")

    const requiredRole = to.meta.role

    // Public route (landing, login, register)
    if (!requiredRole) {
        // Already logged in and trying to visit /login or /register? Send them
        // to their own dashboard instead — no reason to show the login form.
        if (token && (to.path === "/login" || to.path === "/register")) {
            return next(dashboardPathFor(role))
        }
        return next()
    }

    // Protected route, no token at all
    if (!token) {
        return next("/login")
    }

    // Protected route, but wrong role for it
    if (role !== requiredRole) {
        return next(dashboardPathFor(role))
    }

    return next()
})

export default router
