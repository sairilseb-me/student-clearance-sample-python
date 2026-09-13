<script setup>
import { ref, onMounted } from 'vue';

const emit = defineEmits(['change']);

const canvas = ref(null);
let ctx = null;
let drawing = false;
let hasDrawn = false;

onMounted(() => {
    ctx = canvas.value.getContext('2d');
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#1a237e';
});

function pointerPos(event) {
    const rect = canvas.value.getBoundingClientRect();
    return { x: event.clientX - rect.left, y: event.clientY - rect.top };
}

function start(event) {
    drawing = true;
    hasDrawn = true;
    const { x, y } = pointerPos(event);
    ctx.beginPath();
    ctx.moveTo(x, y);
}

function move(event) {
    if (!drawing) return;
    const { x, y } = pointerPos(event);
    ctx.lineTo(x, y);
    ctx.stroke();
}

function stop() {
    if (!drawing) return;
    drawing = false;
    emit('change', hasDrawn ? canvas.value.toDataURL('image/png') : null);
}

function clear() {
    ctx.clearRect(0, 0, canvas.value.width, canvas.value.height);
    hasDrawn = false;
    emit('change', null);
}

defineExpose({ clear });
</script>

<template>
    <div>
        <canvas
            ref="canvas"
            width="360"
            height="140"
            style="border: 1px dashed #9fa8da; border-radius: 4px; touch-action: none; cursor: crosshair; background: #fff"
            @pointerdown="start"
            @pointermove="move"
            @pointerup="stop"
            @pointerleave="stop"
        />
        <div class="mt-2">
            <v-btn size="small" variant="text" @click="clear">Clear signature</v-btn>
        </div>
    </div>
</template>
