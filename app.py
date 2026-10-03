import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta, date, time

# ---------------------------------------------------------
# 1. إعدادات الصفحة الأولية
# ---------------------------------------------------------
st.set_page_config(page_title="HISN Smart Tag Dashboard", page_icon="☢️", layout="wide")

st.title("☢️ منصة تتبع حاويات النفايات المشعة الذكية (HISN Smart Tag)")
st.write("نظام متكامل يستقبل القراءات عبر الـ API / Wi-Fi ويحللها بالذكاء الاصطناعي لحظياً.")

# دالة مخصصة لإنشاء صوت تنبيه متوافق تماماً مع المتصفحات والجوالات (Web Audio API)
def play_alarm_sound():
    sound_js = """
    <script>
    function playBeep() {
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var osc = context.createOscillator();
        var gain = context.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(880, context.currentTime); // تردد التنبيه (880Hz)
        gain.gain.setValueAtTime(1, context.currentTime);
        osc.connect(gain);
        gain.connect(context.destination);
        osc.start();
        osc.stop(context.currentTime + 0.6); // مدة الصوت 0.6 ثانية
    }
    playBeep();
    </script>
    <button onclick="playBeep()" style="
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 8px;
        cursor: pointer;
        width: 100%;
        margin-top: 5px;">
        🔊 اضغطي هنا لسماع/إعادة تشغيل صوت التنبيه
    </button>
    """
    st.components.v1.html(sound_js, height=60)
