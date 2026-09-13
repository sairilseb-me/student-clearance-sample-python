<script setup>
import { useForm } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';

defineOptions({ layout: AuthenticatedLayout });

defineProps({
    offices: {
        type: Array,
        required: true,
    },
});

const form = useForm({
    semester: '',
});

function submit() {
    form.post(route('student.clearance.store'));
}
</script>

<template>
    <div>
        <h1 class="text-h5 font-weight-bold mb-6">Submit Clearance Request</h1>

        <v-row>
            <v-col cols="12" md="6">
                <v-card variant="outlined" class="pa-4">
                    <v-form @submit.prevent="submit">
                        <v-text-field
                            v-model="form.semester"
                            label="Semester"
                            placeholder="e.g. AY 2026-2027, 1st Semester"
                            :error-messages="form.errors.semester"
                            class="mb-2"
                        />
                        <v-btn type="submit" color="indigo-darken-2" size="large" :loading="form.processing">
                            Submit request
                        </v-btn>
                    </v-form>
                </v-card>
            </v-col>

            <v-col cols="12" md="6">
                <p class="text-subtitle-2 mb-2">Your request will route through these offices, in order:</p>
                <v-list density="compact">
                    <v-list-item v-for="office in offices" :key="office.id">
                        <template #prepend>
                            <v-avatar size="24" color="indigo-lighten-4" class="text-caption">
                                {{ office.sign_order }}
                            </v-avatar>
                        </template>
                        <v-list-item-title>{{ office.name }}</v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-col>
        </v-row>
    </div>
</template>
