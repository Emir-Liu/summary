<script setup lang="ts">
import { v4 as uuidv4 } from 'uuid';
import { ref } from 'vue';
let origin_content = ref('')
let user_cmd = ref('')
let outline = ref('')
let thread_id = ref('')
let fullreport = ref('')
let disabled_buildOutline = ref(false)
let disabled_buildReport = ref(true)


// function changeOriginContent() {
//   console.log('修改会议内容')
//   console.log('会议内容：', origin_content.value)
// }

// function changeUserCmd() {
//   console.log('修改用户需求')
//   console.log('用户需求：', user_cmd.value)
// }

function clickBuildOutline() {
  console.log('开始进行总结')
  console.log('origin content:', origin_content.value)
  console.log('user cmd:', user_cmd.value)

  disabled_buildOutline.value = true
  disabled_buildReport.value = false

  thread_id.value = uuidv4()

  let clean_origin_content = origin_content.value.replace(/\r?\n/g, '\\n');
  clean_origin_content = clean_origin_content.replace(/#/g, "-");
  let clean_user_cmd = user_cmd.value.replace(/\r?\n/g, '\\n');
  clean_user_cmd = clean_user_cmd.replace(/#/g, "-");
  const new_url = `http://172.16.0.188:12306/build_outline?thread_id=${thread_id.value}&origin_content=${clean_origin_content}&user_cmd=${clean_user_cmd}`
  console.log('url:', new_url)

  const eventSource = new EventSource(new_url)
  // currentStatus.value = '选择场景中。。。'
  eventSource.onmessage = (event) => {
    console.log('event data:', event.data)
    const input_js = JSON.parse(event.data)
    if (input_js.status == 'finished'){
      outline.value = input_js.content
      eventSource.close()
      disabled_buildOutline.value = false
    } else {
      outline.value = input_js.content
    }
  };
  eventSource.onerror = (error) => {
      // eventData.value = ''
      // console.error('SSE error:', error);
      // loading_status.value = false
      console.log('意外结束')
      eventSource.close();
      disabled_buildOutline.value = false
  };
}

function clickBuildReport() {
  console.log('开始生成报告')
  console.log('outline:', outline.value)

  disabled_buildReport.value = true

  let clean_outline = outline.value.replace(/\r?\n/g, '\\n');
  clean_outline = clean_outline.replace(/#/g, "-");

  console.log('outline:', outline.value)
  const new_url = `http://172.16.0.188:12306/build_report?thread_id=${thread_id.value}&human_response=${clean_outline}`
  // const new_url = `http://172.16.0.188:12306/build_outline?thread_id=${thread_id.value}&origin_content=${origin_content.value}&user_cmd=${user_cmd.value}`
  console.log('url:', new_url)

  const eventSource = new EventSource(new_url)
  // currentStatus.value = '选择场景中。。。'
  eventSource.onmessage = (event) => {
    console.log('event data:', event.data)
    const input_js = JSON.parse(event.data)
    if (input_js.status == 'finished'){
      fullreport.value = input_js.content
      eventSource.close()
      disabled_buildReport.value = false
    } else {
      fullreport.value = input_js.content
    }
  };
  eventSource.onerror = (error) => {
      // eventData.value = ''
      // console.error('SSE error:', error);
      // loading_status.value = false
      console.log('意外结束')
      eventSource.close();
      disabled_buildReport.value = false
  };
}


</script>

<template>
  <h1>会议纪要总结</h1>

  <div>
    <div>
      <p>会议内容:</p>
      <textarea placeholder="输入会议内容" v-model="origin_content"></textarea>
    </div>

    <div>
      <p>定制化要求:</p>
      <textarea placeholder="输入定制化要求" v-model="user_cmd"></textarea>
    </div>

    <br>
    <button @click="clickBuildOutline" :disabled="disabled_buildOutline">开始进行总结</button>
  </div>

  <div>
    <p>会议内容大纲：</p>
    <textarea placeholder="开始总结后，将自动生成会议内容大纲，用户可以根据自己的要求手动修改大纲" v-model="outline"></textarea>
    <br>
    <br>
    <button @click="clickBuildReport" :disabled="disabled_buildReport">生成完整报告</button>
  </div>

  <div>
    <p>完整报告：</p>
    <textarea placeholder="这里是完整的报告" v-model="fullreport"></textarea>
  </div>

</template>

<style scoped>
</style>
