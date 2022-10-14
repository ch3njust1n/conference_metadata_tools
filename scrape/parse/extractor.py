import cv2
import layoutparser as lp


def main():
	image = cv2.imread('001.jpg')
	image = image[..., ::-1]
	model = lp.Detectron2LayoutModel( config_path ='lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config', label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
	layout = model.detect(image)
	processed = lp.draw_box(image, layout, box_width=3)
	processed.show()

	text_blocks = lp.Layout([b for b in layout if b.type=='Text'])
	figure_blocks = lp.Layout([b for b in layout if b.type=='Figure'])

	text_blocks = lp.Layout([b for b in text_blocks if not any(b.is_in(b_fig) for b_fig in figure_blocks)])
	lp.draw_box(image, layout, box_width=3)

	h, w = image.shape[:2]

	left_interval = lp.Interval(0, w/2*1.05, axis='x').put_on_canvas(image)

	left_blocks = text_blocks.filter_by(left_interval, center=True)
	left_blocks.sort(key = lambda b:b.coordinates[1])

	right_blocks = [b for b in text_blocks if b not in left_blocks]
	right_blocks.sort(key = lambda b:b.coordinates[1])

	# And finally combine the two list and add the index
	# according to the order
	text_blocks = lp.Layout([b.set(id = idx) for idx, b in enumerate(left_blocks + right_blocks)])

	lp.draw_box(image, text_blocks,
            box_width=3,
            show_element_id=True)

	ocr_agent = lp.TesseractAgent(languages='eng')


	for block in text_blocks:
	    segment_image = (block.pad(left=5, right=5, top=5, bottom=5).crop_image(image))
	    text = ocr_agent.detect(segment_image)
	    block.set(text=text, inplace=True)


	for txt in text_blocks.get_texts():
		print(txt, end='\n---\n')


if __name__ == "__main__":
	main()