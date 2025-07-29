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
		Q='RGB';P=False;J=param_is_ref;I=param_reader;R=F if J else I;S=F if not J else I;Y=F.reader_options;Z=P;a=P;A=R.img;D=S.img;b,K=compare_floats.compare_errors.add_group('pixels','img')
		if A.size!=D.size:K.error=f"Image sizes differ: {A.size} != {D.size}";return
		T,U=A.size;E=0;V=10;L=[]
		for B in range(U):
			for C in range(T):
				M=A.getpixel((C,B));N=D.getpixel((C,B))
				if M!=N:
					if E<V:L.append(((C,B),M,N))
					E+=1
		G=None
		if E:
			O=f"Found {E} different pixels.";K.error=O;logging.debug(O)
			for((C,B),W,X)in L:logging.debug(f"Pixel at ({C}, {B}) differs: {W} vs {X}")
			H=ImageChops.difference(A.convert(Q),D.convert(Q));G=data_png_base64(H)
		else:logging.debug('No pixel differences found.')
		if G:return{'diff_image':{'data':G,'width':H.width,_A:H.height}}
	def class_info(A):return{'metrics':A.metrics}