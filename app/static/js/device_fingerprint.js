/** 
 * Pro版设备指纹生成工具 (V5 - GPU/CPU Hard Core) 
 * 逻辑：HardwareConcurrency + Timezone + WebGL Renderer 
 */ 
(function(window) { 
    function simpleHash(str) { 
        let hash = 0; 
        for (let i = 0; i < str.length; i++) { 
            hash = ((hash << 5) - hash) + str.charCodeAt(i); 
            hash = hash & hash; 
        } 
        return (hash >>> 0).toString(16); 
    } 

    function getWebglRenderer() { 
        try { 
            const canvas = document.createElement('canvas'); 
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl'); 
            if (!gl) return 'no_webgl'; 
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info'); 
            return debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'unknown_renderer'; 
        } catch (e) { return 'webgl_error'; } 
    } 

    function getDeviceId() { 
        try { 
            // 核心特征组合 
            const components = [ 
                navigator.hardwareConcurrency || 'unknown', 
                new Date().getTimezoneOffset(), 
                getWebglRenderer() 
            ]; 
            // 生成指纹: fp_v5_ + hash 
            const fingerprint = 'fp_v5_' + simpleHash(components.join('||')); 
            
            // 缓存处理 
            localStorage.setItem('device_fingerprint_v5', fingerprint); 
            return fingerprint; 
        } catch (e) { 
            return 'error_' + Date.now(); 
        } 
    } 

    window.DeviceFingerprint = { getDeviceId: getDeviceId }; 
})(window); 
