from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
import json
import hashlib
import logging
from .models import License

logger = logging.getLogger(__name__)

def verify_api_key(request):
    """Xác thực API key từ request"""
    client_key = request.headers.get('X-API-Key') or request.GET.get('api_key')
    server_key = settings.API_KEY 


    return client_key == server_key

@csrf_exempt  # Bỏ qua CSRF token (cần cho API public)
@require_http_methods(["POST","GET"])  # Chỉ cho phép GET và POST
def verify_license(request):
    print(request.method)
    """
    API endpoint để xác thực license key
    URL: /api/verify-license/
    Method: GET hoặc POST
    """
    # Bước 1: Kiểm tra API key
    if not verify_api_key(request):
        return JsonResponse({
            'success': False,
            'error': 'Invalid API key',
            'message': 'API key không hợp lệ'
        }, status=401)
    
    # Bước 2: Lấy dữ liệu từ request
    if request.method == 'POST':
        # print("post1")
        # Kiểm tra Content-Type để xử lý đúng định dạng
        content_type = request.META.get('CONTENT_TYPE', '').lower() 
        # print("content_type:", content_type) 
        
        if 'application/json' in content_type:
            # Xử lý JSON
            try:
                # print("request:",request.body.decode('utf-8'))
                rq = request.body.decode('utf-8')
                data = json.loads(rq)
                # print("data:", data)
                license_key = data.get('license_key')
                hardware_id = data.get('hardware_id')
                print("data:", license_key, hardware_id)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in request: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON',
                    'message': 'Dữ liệu JSON không hợp lệ'
                }, status=400)
        else:
            # Xử lý Form Data (multipart/form-data hoặc application/x-www-form-urlencoded)
            license_key = request.POST.get('license_key')
            hardware_id = request.POST.get('hardware_id')
    else:  # GET request
        # print("get")
        license_key = request.GET.get('license_key')
        hardware_id = request.GET.get('hardware_id')
    
    # Bước 3: Kiểm tra license_key có được cung cấp không
    if not license_key:
        return JsonResponse({
            'success': False,
            'error': 'Missing license_key',
            'message': 'Vui lòng cung cấp license_key'
        }, status=400)
    
    # Bước 4: Tìm và kiểm tra license trong database
    try:
        license_obj = License.objects.get(key=license_key)
        
        # Kiểm tra trạng thái
        if license_obj.status != 'active':
            #nếu license chưa có hardware_id  thì gán và kích hoạt 
            if hardware_id:
                license_obj.hardware_id = hardware_id
                license_obj.status = 'active'
                license_obj.save()
                return JsonResponse({
                    'success': True,
                    'valid': True,
                    'message': 'Kích hoạt thành công',
                    'license_key': license_key,
                    'provided_hardware_id': hardware_id
                }, status=200)

            #nếu license đã có hardware_id thì báo lỗi bị license không hoạt động
            return JsonResponse({
                'success': False,
                'valid': False,
                'error': 'License inactive',
                'message': 'License không hoạt động',
                'license_key': license_key,
                'status': license_obj.status
            }, status=200)
        
        # Kiểm tra ngày hết hạn
        today = timezone.now().date()
        if license_obj.expiration_date < today:
            return JsonResponse({
                'success': False,
                'valid': False,
                'error': 'License expired',
                'message': 'License đã hết hạn',
                'license_key': license_key,
                'expiration_date': license_obj.expiration_date.isoformat(),
                'current_date': today.isoformat()
            }, status=200)
        
        # Kiểm tra hardware_id nếu được cung cấp
        if hardware_id:
            if license_obj.hardware_id and license_obj.hardware_id != hardware_id:
                return JsonResponse({
                    'success': False,
                    'valid': False,
                    'error': 'Hardware ID mismatch',
                    'message': 'Hardware ID không khớp',
                    'license_key': license_key,
                    # 'expected_hardware_id': license_obj.hardware_id,
                    'provided_hardware_id': hardware_id
                }, status=200)
            # elif not license_obj.hardware_id:
            #     # Gán hardware_id nếu chưa có
            #     license_obj.hardware_id = hardware_id
            #     license_obj.save()
            #     return JsonResponse({
            #         'success': True,
            #         'valid': False,
            #         # 'error': 'Hardware ID mismatch',
            #         'message': 'Kích hoạt thành công',
            #         'license_key': license_key,
            #         # 'expected_hardware_id': license_obj.hardware_id,
            #         'provided_hardware_id': hardware_id
            #     }, status=200)
        # License hợp lệ - trả về thành công
        return JsonResponse({
            'success': True,
            'valid': True,
            'message': 'License hợp lệ',
            'license_key': license_key,
            'status': license_obj.status,
            'expiration_date': license_obj.expiration_date.isoformat(),
            # 'hardware_id': license_obj.hardware_id or hardware_id,
            'created_at': license_obj.created_at.isoformat()
        }, status=200)
        
    except License.DoesNotExist:
        return JsonResponse({
            'success': False,
            'valid': False,
            'error': 'License not found',
            'message': 'License không tồn tại',
            'license_key': license_key
        }, status=200)
    except Exception as e:
        # Log chi tiết lỗi ở server, không gửi ra client
        logger.error(f"Server error in verify_license: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Server error',
            'message': 'Lỗi server. Vui lòng thử lại sau.'
        }, status=500)



#ham kich hoat license
