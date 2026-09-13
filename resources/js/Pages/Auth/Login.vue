<script setup>
import { useForm } from '@inertiajs/vue3';

const form = useForm({
    email: '',
    password: '',
});

function submit() {
    form.post(route('login'), {
        onFinish: () => form.reset('password'),
    });
}

const demoAccounts = [
    ['Student', 'student@demo.test'],
    ['Adviser', 'adviser@demo.test'],
    ['Library', 'library@demo.test'],
    ['Treasurer', 'treasurer@demo.test'],
    ['Guidance', 'guidance@demo.test'],
];

function fillDemo(email) {
    form.email = email;
    form.password = 'password';
}
</script>

<template>
    <v-app>
        <v-main class="d-flex align-center justify-center" style="min-height: 100vh; background: #f3f4f8">
            <v-card width="420" elevation="4" class="pa-6">
                <v-card-title class="text-h5 font-weight-bold mb-1">Student Clearance</v-card-title>
                <v-card-subtitle class="mb-4">Sign in to continue</v-card-subtitle>

                <v-form @submit.prevent="submit">
                    <v-text-field
                        v-model="form.email"
                        label="Email"
                        type="email"
                        :error-messages="form.errors.email"
                        autofocus
                        class="mb-2"
                    />
                    <v-text-field
                        v-model="form.password"
                        label="Password"
                        type="password"
                        :error-messages="form.errors.password"
                        class="mb-2"
                    />
                    <v-btn type="submit" color="indigo-darken-2" block size="large" :loading="form.processing">
                        Log in
                    </v-btn>
                </v-form>

                <v-divider class="my-5" />

                <p class="text-caption text-medium-emphasis mb-2">Demo accounts (password: "password")</p>
                <v-chip
                    v-for="[label, email] in demoAccounts"
                    :key="email"
                    class="mr-2 mb-2"
                    size="small"
                    variant="outlined"
                    @click="fillDemo(email)"
                >
                    {{ label }}
                </v-chip>
            </v-card>
        </v-main>
    </v-app>
</template>
