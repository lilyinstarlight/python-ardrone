#include <Python.h>

#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavutil/frame.h>
#include <libswscale/swscale.h>

struct PaVE {
	uint8_t signature[4]; //"PaVE"
	uint8_t version; //protocol version
	uint8_t video_codec; //codec of frame
	uint16_t header_size; //size of this header
	uint32_t payload_size; //size of payload frame
	uint16_t encoded_stream_width; //encoded width
	uint16_t encoded_stream_height; //encoded height
	uint16_t display_width; //actual width
	uint16_t display_height; //actual height

	uint32_t frame_number; //current frame
	uint32_t timestamp; //timestamp in milliseconds of frame
	uint8_t total_chunks; //number of packets for frame (unused)
	uint8_t chunck_index; //current packet number for frame (unused)
	uint8_t frame_type; //I-frame or P-frame
	uint8_t control; //control command (e.g. end of stream, advertised frames)
	uint32_t stream_byte_position_lw; //lower word of byte position in stream
	uint32_t stream_byte_position_uw; //upper word of byte position in stream
	uint16_t stream_id; //current stream this frame is associated with
	uint8_t total_slices; //number of slices in frame
	uint8_t slice_index; //position of current slice
	uint8_t header1_size; //size of SPS in frame (h.264 only)
	uint8_t header2_size; //size of PPS in frame (h.264 only)
	uint8_t reserved1[2]; //padding to align to 48 bytes
	uint32_t advertised_size; //size of advertised frame
	uint8_t reserved2[12]; //padding to align to 64 bytes
};

static PyObject * video_decode(PyObject * self, PyObject * args);

static PyMethodDef VideoMethods[] = {
	{"decode",  video_decode, METH_VARARGS, "decode a PaVE video packet into an RGB image buffer"},
	{NULL, NULL, 0, NULL}
};

static PyObject * VideoDecodeError;

AVCodec * codec;
AVCodecContext * context;
AVFrame * frame;
SwsContext * sws_context;

PyMODINIT_FUNC initvideo(void) {
	PyObject * module;

	module = Py_InitModule("video", VideoMethods);
	if(module == NULL)
		return;

	VideoDecodeError = PyErr_NewException("video.DecodeError", NULL, NULL);
	Py_INCREF(VideoDecodeError);
	PyModule_AddObject(module, "DecodeError", VideoDecodeError);

	av_register_all();
	avcodec_register_all();

	codec = avcodec_find_decoder(AV_CODEC_ID_H264);
	if(!codec) {
		PyErr_SetString(VideoDecodeError, "could not find h.264 decoder");
		return;
	}

	context = avcodec_alloc_context3(codec);
	if(!context) {
		PyErr_NoMemory();
		return;
	}

	avcodec_get_context_defaults3(context, codec);
	if(avcodec_open2(context, codec, NULL) < 0) {
		PyErr_SetString(VideoDecodeError, "could not open h.264 codec");
		return;
	}

	frame = av_frame_alloc();
	if(!frame) {
		PyErr_NoMemory();
		return;
	}
}

static PyObject * video_decode(PyObject * self, PyObject * args) {
	const char * data;
	int data_size;

	struct PaVE header;
	const char * payload;

	AVPacket packet;

	int got_frame;
	int frame_size;

	const char * image;
	int image_width;
	int image_height;

	if(!PyArg_ParseTuple(args, "s#", &data, &data_size))
		return NULL;

	header = *data;
	payload = data + header.header_size;

	if(memcmp(header.signature, "PaVE", 4) != 0) {
		PyErr_SetString(VideoDecodeError, "packet did not have correct signature");
		return NULL;
	}

	if(header.header_size + header.payload_size != data_size) {
		PyErr_SetString(VideoDecodeError, "packet size did not match expected size from header");
		return NULL;
	}

	av_init_packet(&packet);

	packet.pts = AV_NOPTS_VALUE;
	packet.dts = AV_NOPTS_VALUE;
	packet.data = payload;
	packet.size = header.payload_size;

	frame_size = avcodec_decode_video2(context, frame, &got_frame, &packet);
	if(frame_size < 0 || !got_frame) {
		PyErr_SetString(VideoDecodeError, "could not decode frame");
		return NULL;
	}

	image_width = frame->width;
	image_height = frame->height;

	sws_context = sws_getCachedContext(sws_context, context->width, context->height, AV_PIX_FMT_YUV420P, context->width, context->height, AV_PIX_FMT_BGR24, SWS_FAST_BILINEAR, 0, 0, 0);
	sws_scale(sws_context, frame->data, frame->linesize, 0, frame->height, image, image_width);

	return Py_BuildValue("iis#", image_width, image_height, image, image_size);
}
