<script setup>
import { ref, reactive } from 'vue';
import { router } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import SignaturePad from '@/Components/SignaturePad.vue';

defineOptions({ layout: AuthenticatedLayout });

const props = defineProps({
    clearanceApproval: {
        type: Object,
        required: true,
    },
});

const signatureDataUrl = ref(null);
const placed = reactive({ top: 220, left: 220 });
const dragging = ref(false);
const processing = ref(false);
const rejectDialog = ref(false);
const remarks = ref('');

function onSignatureChange(dataUrl) {
    signatureDataUrl.value = dataUrl;
}

function startDrag(event) {
    if (!signatureDataUrl.value) return;
    dragging.value = true;
    event.preventDefault();
}

function onDrag(event) {
    if (!dragging.value) return;
    const docEl = event.currentTarget;
    const rect = docEl.getBoundingClientRect();
    placed.left = Math.min(Math.max(event.clientX - rect.left - 70, 0), rect.width - 140);
    placed.top = Math.min(Math.max(event.clientY - rect.top - 20, 0), rect.height - 40);
}

function stopDrag() {
    dragging.value = false;
}

function confirmSign() {
    processing.value = true;
    router.patch(
        route('approver.approvals.update', props.clearanceApproval.id),
        {
            action: 'sign',
            signature_data: signatureDataUrl.value,
        },
        { onFinish: () => (processing.value = false) },
    );
}

function confirmReject() {
    processing.value = true;
    router.patch(
        route('approver.approvals.update', props.clearanceApproval.id),
        {
            action: 'reject',
            remarks: remarks.value,
        },
        { onFinish: () => (processing.value = false) },
    );
}
</script>

<template>
    <div>
        <h1 class="text-h5 font-weight-bold mb-6">
            Sign-off · {{ clearanceApproval.clearance_request.student.name }}
        </h1>

        <v-row>
            <v-col cols="12" md="7">
                <p class="text-subtitle-2 mb-2">Drag your signature onto the form to place it, then confirm.</p>
                <div
                    class="document-preview"
                    @pointermove="onDrag"
                    @pointerup="stopDrag"
                    @pointerleave="stopDrag"
                >
                    <div class="text-overline text-center pt-4">Clearance Form</div>
                    <div class="text-center text-body-2 mb-2">
                        {{ clearanceApproval.clearance_request.student.name }} —
                        {{ clearanceApproval.clearance_request.semester }}
                    </div>
                    <v-divider class="mx-6" />
                    <div class="px-6 pt-4 text-body-2">
                        Office: <strong>{{ clearanceApproval.office.name }}</strong>
                    </div>
                    <div class="px-6 text-caption text-medium-emphasis">Approver signature required below</div>

                    <img
                        v-if="signatureDataUrl"
                        :src="signatureDataUrl"
                        class="placed-signature"
                        :style="{ top: placed.top + 'px', left: placed.left + 'px' }"
                        draggable="false"
                        @pointerdown="startDrag"
                    />
                </div>
            </v-col>

            <v-col cols="12" md="5">
                <v-card variant="outlined" class="pa-4 mb-4">
                    <p class="text-subtitle-2 mb-2">1. Draw your signature</p>
                    <SignaturePad @change="onSignatureChange" />
                </v-card>

                <v-btn
                    color="indigo-darken-2"
                    size="large"
                    block
                    class="mb-2"
                    :disabled="!signatureDataUrl"
                    :loading="processing"
                    @click="confirmSign"
                >
                    Confirm & sign
                </v-btn>
                <v-btn color="red-darken-2" variant="outlined" block @click="rejectDialog = true">
                    Reject request
                </v-btn>
            </v-col>
        </v-row>

        <v-dialog v-model="rejectDialog" max-width="420">
            <v-card>
                <v-card-title>Reject this request</v-card-title>
                <v-card-text>
                    <v-textarea v-model="remarks" label="Reason" rows="3" />
                </v-card-text>
                <v-card-actions>
                    <v-spacer />
                    <v-btn variant="text" @click="rejectDialog = false">Cancel</v-btn>
                    <v-btn color="red-darken-2" :loading="processing" @click="confirmReject">Reject</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<style scoped>
.document-preview {
    position: relative;
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    height: 420px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    touch-action: none;
}

.placed-signature {
    position: absolute;
    height: 40px;
    cursor: grab;
    user-select: none;
}
</style>
