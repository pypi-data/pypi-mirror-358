from google.colab.patches import cv2_imshow
from google.colab import output
from IPython.display import display, Javascript, clear_output

def setMouseCallback(imgs, onmouse=None):
  if onmouse:
    js_code = Javascript('''
      var dragging = false;
      function callback(e, event_name){
          var x = e.offsetX;
          var y = e.offsetY;
          var event=0
          var flag=0;

          if(event_name =='mousedown'){
            if(e.button==0){
              event=1;

              dragging=true;
            }else if(e.button==2){
              event=2;
              flag+=2
            }
          }else if(event_name=='mouseup'){
            if(e.button==0){
              event=4;

              if(dragging) dragging=false;
            }else if(e.button==2){
              event=5;

            }
          }else if(event_name=='mousemove'){
            event=0;
            if(dragging){
              flag+=1
            }
            console.log(e.button)
          }

          if(e.altKey){
            flag+=32;
          }
          if(e.ctrlKey){
            flag+=8;
          }
          if(e.shiftKey){
            flag+=16
          }
          google.colab.kernel.invokeFunction('notebook.onmouse', [event, x, y, flag, null], {});
      }
      window.setTimeout(()=>{
        var img = document.querySelector('#output-area img');
        img.draggable=false;
        img.addEventListener('mousedown',(e)=>{
          callback(e, 'mousedown')
        });
        img.addEventListener('contextmenu', (e)=>{e.preventDefault();})
        img.addEventListener('mouseup', (e)=>{
          callback(e, 'mouseup')
        });
        img.addEventListener('mousemove',(e)=>{
          console.log('move')
          callback(e, 'mousemove')
        });
      }, 0);
    ''')
    cv2_imshow(imgs)
    output.register_callback('notebook.onmouse', onmouse)
    display(js_code)
  else:
    print('no mouse event!!')



def selectROI(img, callback):
    cv2_imshow(img) #출력 영역에 이미지 표시
    if callback==None:
      print('no callback registered.')
      return
      
    output.register_callback('notebook.onmouse', callback) #calab output으로 콜랩 등록
    
    js_code = """
    window.setTimeout(() => { //렌더링까지 시간이 걸려서 10ms 대기 후 실행
        let img = document.querySelector('#output-area img');//cv_imshow()를 통해 출력되는 이미지 요소
        if (!img) return;

        img.draggable = false;
        img.style.cursor = 'crosshair'; 
        let canvas = document.createElement('canvas');
        let ctx = canvas.getContext('2d');
        let rect = {};
        let isDrawing = false;
        let boxColor = 'blue'
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.style.position = 'absolute';
        canvas.style.top = img.offsetTop + 'px';
        canvas.style.left = img.offsetLeft + 'px';
        canvas.style.pointerEvents = 'none';
        
        //canvas.style.backgroundColor = 'rgba(0, 0, 0, 0.3)'; // 반투명 배경 적용
        
        document.body.appendChild(canvas);

        function startDraw(event) {
            console.log(event);
            rect.startX = event.offsetX;
            rect.startY = event.offsetY;
            isDrawing = true;
        }

        function draw(event) {
            if (!isDrawing) return;
            rect.w = event.offsetX - rect.startX;
            rect.h = event.offsetY - rect.startY;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = boxColor;
            ctx.lineWidth = 2;
            ctx.strokeRect(rect.startX, rect.startY, rect.w, rect.h);
        }

        function stopDraw(event) {
            if (isDrawing){
              boxColor= 'red'
              draw(event);
              boxColor= 'blue'
              isDrawing = false;
              
              //document.body.removeChild(canvas);
              google.colab.kernel.invokeFunction('notebook.onmouse', [rect.startX, rect.startY, rect.w, rect.h], {});
            }
            
        }

        img.addEventListener('mousedown', startDraw);
        img.addEventListener('mousemove', draw);
        img.addEventListener('mouseup', stopDraw);
    }, 10);
    """
    display(Javascript(js_code))