<script setup>
import { computed } from 'vue';
import { usePage, router } from '@inertiajs/vue3';
import AiClearanceAssistant from '@/Components/AiClearanceAssistant.vue';

const page = usePage();
const user = computed(() => page.props.auth.user);

const studentNav = [{ title: 'Dashboard', href: route('student.dashboard') }];
const approverNav = [{ title: 'Dashboard', href: route('approver.dashboard') }];

const navItems = computed(() => (user.value?.role === 'approver' ? approverNav : studentNav));

function logout() {
    router.post(route('logout'));
}
</script>

<template>
    <v-app>
        <v-app-bar color="indigo-darken-2" density="comfortable" flat>
            <v-app-bar-title>
                <span class="font-weight-bold">Student Clearance</span>
            </v-app-bar-title>

            <template #append>
                <span class="text-body-2 mr-4">{{ user?.name }} · {{ user?.role }}</span>
                <v-btn variant="text" @click="logout">Log out</v-btn>
            </template>
        </v-app-bar>

        <v-navigation-drawer permanent>
            <v-list nav density="comfortable">
                <v-list-item
                    v-for="item in navItems"
                    :key="item.title"
                    :title="item.title"
                    @click="router.visit(item.href)"
                />
            </v-list>
        </v-navigation-drawer>

        <v-main>
            <v-container fluid class="pa-6">
                <slot />
            </v-container>
        </v-main>

        <AiClearanceAssistant />
    </v-app>
</template>
