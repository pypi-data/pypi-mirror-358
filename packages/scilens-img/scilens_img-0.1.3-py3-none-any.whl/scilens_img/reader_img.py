_A='height'
import logging
from scilens.readers.reader_interface import ReaderInterface
from scilens.components.compare_floats import CompareFloats
from PIL import Image,ImageChops
import io,base64
def data_png_base64(img):A=io.BytesIO();img.save(A,format='PNG');B=base64.b64encode(A.getvalue()).decode('utf-8');return f"data:image/png;base64,{B}"
class ReaderImg(ReaderInterface):
	configuration_type_code='img';category='binary';extensions=['PNG','JPG','JPEG','BMP','TIFF','TIF']
	def close(A):0
	def read(A,reader_options):A.reader_options=reader_options;A.img=Image.open(A.origin.path).convert('RGBA');A.metrics=None;A.reader_info['width']=A.img.width;A.reader_info[_A]=A.img.height
	def compare(F,compare_floats,param_reader,param_is_ref=True):
		P='RGB';O=False;J=param_is_ref;I=param_reader;Q=F if J else I;R=F if not J else I;W=F.reader_options;X=O;Y=O;A=Q.img;D=R.img;Z,K=compare_floats.compare_errors.add_group('pixels','img')
		if A.size!=D.size:K.error=f"Image sizes differ: {A.size} != {D.size}";return
		S,T=A.size;E=[]
		for B in range(T):
			for C in range(S):
				L=A.getpixel((C,B));M=D.getpixel((C,B))
				if L!=M:E.append(((C,B),L,M))
		G=None
		if E:
			N=f"Found {len(E)} different pixels.";K.error=N;logging.debug(N)
			for((C,B),U,V)in E[:10]:logging.debug(f"Pixel at ({C}, {B}) differs: {U} vs {V}")
			H=ImageChops.difference(A.convert(P),D.convert(P));G=data_png_base64(H)
		else:logging.debug('No pixel differences found.')
		if G:return{'diff_image':{'data':G,'width':H.width,_A:H.height}}
	def class_info(A):return{'metrics':A.metrics}