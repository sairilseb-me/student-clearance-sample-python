<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';

defineOptions({ layout: AuthenticatedLayout });

defineProps({
    clearanceRequest: {
        type: Object,
        required: true,
    },
});

function printClearance() {
    window.print();
}
</script>

<template>
    <div>
        <h1 class="text-h5 font-weight-bold mb-6">Signed Clearance</h1>

        <v-card variant="outlined" class="pa-8 mx-auto" max-width="700">
            <div class="text-center mb-6">
                <div class="text-overline">Official Clearance Form</div>
                <div class="text-h6 font-weight-bold">{{ clearanceRequest.student.name }}</div>
                <div class="text-body-2 text-medium-emphasis">{{ clearanceRequest.semester }}</div>
            </div>

            <v-divider class="mb-4" />

            <v-table density="comfortable">
                <thead>
                    <tr>
                        <th>Office</th>
                        <th>Signed by</th>
                        <th>Date</th>
                        <th>Signature</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="approval in clearanceRequest.approvals" :key="approval.id">
                        <td>{{ approval.office.name }}</td>
                        <td>{{ approval.approver?.name ?? '—' }}</td>
                        <td>{{ approval.signed_at ? new Date(approval.signed_at).toLocaleDateString() : '—' }}</td>
                        <td>
                            <img
                                v-if="approval.signature_data"
                                :src="approval.signature_data"
                                alt="signature"
                                style="height: 40px"
                            />
                            <span v-else>—</span>
                        </td>
                    </tr>
                </tbody>
            </v-table>

            <div class="text-center mt-8">
                <v-chip color="green-darken-1" size="large">Fully Cleared</v-chip>
            </div>
        </v-card>

        <div class="text-center mt-4">
            <v-btn color="indigo-darken-2" variant="tonal" @click="printClearance">Print / Save as PDF</v-btn>
        </div>
    </div>
</template>
