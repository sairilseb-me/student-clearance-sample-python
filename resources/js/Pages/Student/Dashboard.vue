<script setup>
import { computed } from 'vue';
import { router } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';

defineOptions({ layout: AuthenticatedLayout });

const props = defineProps({
    clearanceRequest: {
        type: Object,
        default: null,
    },
});

const statusColor = {
    pending: 'amber-darken-2',
    signed: 'green-darken-1',
    rejected: 'red-darken-2',
    approved: 'green-darken-1',
};

const canSubmitNew = computed(() => !props.clearanceRequest || props.clearanceRequest.status === 'approved');

function startRequest() {
    router.visit(route('student.clearance.create'));
}

function viewPdf() {
    router.visit(route('student.clearance.show', props.clearanceRequest.id));
}

function requestResubmission(approvalId) {
    router.post(route('student.approvals.resubmit', approvalId));
}
</script>

<template>
    <div>
        <h1 class="text-h5 font-weight-bold mb-6">My Clearance</h1>

        <v-alert v-if="!clearanceRequest" type="info" variant="tonal" class="mb-4">
            You haven't submitted a clearance request yet.
        </v-alert>

        <v-btn v-if="canSubmitNew" color="indigo-darken-2" size="large" class="mb-6" @click="startRequest">
            Submit {{ clearanceRequest ? 'new' : '' }} clearance request
        </v-btn>

        <template v-if="clearanceRequest">
            <v-card class="mb-6" variant="outlined">
                <v-card-item>
                    <v-card-title>{{ clearanceRequest.semester }}</v-card-title>
                    <v-card-subtitle>
                        Overall status:
                        <v-chip :color="statusColor[clearanceRequest.status]" size="small" class="ml-1">
                            {{ clearanceRequest.status }}
                        </v-chip>
                    </v-card-subtitle>
                </v-card-item>
                <v-card-actions v-if="clearanceRequest.status === 'approved'">
                    <v-btn color="indigo-darken-2" variant="tonal" @click="viewPdf">
                        View / download signed clearance
                    </v-btn>
                </v-card-actions>
                <v-alert v-if="clearanceRequest.status === 'rejected'" type="warning" variant="tonal" class="ma-4 mt-0">
                    One or more offices rejected this request. Resolve the issue with that office, then request a
                    resubmission below so they can review it again.
                </v-alert>
            </v-card>

            <v-row>
                <v-col v-for="approval in clearanceRequest.approvals" :key="approval.id" cols="12" sm="6" md="3">
                    <v-card variant="outlined">
                        <v-card-item>
                            <v-card-title class="text-subtitle-1">{{ approval.office.name }}</v-card-title>
                            <v-chip :color="statusColor[approval.status]" size="small" class="mt-2">
                                {{ approval.status }}
                            </v-chip>
                        </v-card-item>
                        <v-card-text v-if="approval.status === 'signed'" class="text-caption">
                            Signed by {{ approval.approver?.name }}
                        </v-card-text>
                        <template v-else-if="approval.status === 'rejected'">
                            <v-card-text class="text-caption">
                                Rejected by {{ approval.approver?.name }}
                                <span v-if="approval.remarks">— "{{ approval.remarks }}"</span>
                            </v-card-text>
                            <v-card-actions>
                                <v-btn
                                    color="indigo-darken-2"
                                    variant="tonal"
                                    size="small"
                                    @click="requestResubmission(approval.id)"
                                >
                                    Request resubmission
                                </v-btn>
                            </v-card-actions>
                        </template>
                    </v-card>
                </v-col>
            </v-row>
        </template>
    </div>
</template>
