'''
Extract text from specified sections
'''

import cv2
import layoutparser as lp


class OCRExtractor(object):
	def __init__(self,
				 target_section,
				 preview=False,
				 config_path='lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config'):
		self.model = lp.Detectron2LayoutModel( config_path=config_path, label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
		self.target_section = target_section.title()
		self.preview = preview
	
 
	'''
	Extract text from sections. May return false positives and may not detect false negatives.
	
	input:
	data (str, np.array) If string, read the file path. Else if it's a numpy array, continue
 
	output:
	results (list) List of text from potential sections
 	'''
	def extract(self, data):
		self.image = cv2.imread(data) if isinstance(data, str) else data
		self.image = self.image[..., ::-1]
		layout = self.model.detect(self.image)
  
		title_blocks = lp.Layout([b for b in layout if b.type==self.target_section])
		figure_blocks = lp.Layout([b for b in layout if b.type=='Figure'])
		title_blocks = lp.Layout([b for b in title_blocks if not any(b.is_in(b_fig) for b_fig in figure_blocks)])
		
		if self.preview:
			lp.draw_box(self.image, layout, box_width=3)

		h, w = self.image.shape[:2]

		left_interval = lp.Interval(0, w/2*1.05, axis='x').put_on_canvas(self.image)
		left_blocks = title_blocks.filter_by(left_interval, center=True)
		left_blocks.sort(key = lambda b:b.coordinates[1])
	
		right_blocks = [b for b in title_blocks if b not in left_blocks]
		right_blocks.sort(key = lambda b:b.coordinates[1])

		# And finally combine the two list and add the index
		title_blocks = lp.Layout([b.set(id = idx) for idx, b in enumerate(left_blocks + right_blocks)])

		if self.preview:
			processed = lp.draw_box(self.image, title_blocks, box_width=3, show_element_id=True)
			processed.show()

		ocr_agent = lp.TesseractAgent(languages='eng')

		for block in title_blocks:
			segment_image = (block.pad(left=5, right=5, top=5, bottom=5).crop_image(self.image))
			text = ocr_agent.detect(segment_image)
			block.set(text=text, inplace=True)

		return [txt for txt in title_blocks.get_texts()]