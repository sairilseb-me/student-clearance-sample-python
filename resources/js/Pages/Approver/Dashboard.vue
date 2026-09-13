<script setup>
import { router } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';

defineOptions({ layout: AuthenticatedLayout });

defineProps({
    pendingApprovals: {
        type: Array,
        required: true,
    },
});

function review(approvalId) {
    router.visit(route('approver.approvals.show', approvalId));
}
</script>

<template>
    <div>
        <h1 class="text-h5 font-weight-bold mb-6">Pending Clearance Requests</h1>

        <v-alert v-if="pendingApprovals.length === 0" type="success" variant="tonal">
            No pending requests. You're all caught up.
        </v-alert>

        <v-row>
            <v-col v-for="approval in pendingApprovals" :key="approval.id" cols="12" sm="6" md="4">
                <v-card variant="outlined">
                    <v-card-item>
                        <v-card-title>{{ approval.clearance_request.student.name }}</v-card-title>
                        <v-card-subtitle>{{ approval.clearance_request.semester }}</v-card-subtitle>
                    </v-card-item>
                    <v-card-actions>
                        <v-btn color="indigo-darken-2" variant="tonal" @click="review(approval.id)">
                            Review & sign
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>
    </div>
</template>
