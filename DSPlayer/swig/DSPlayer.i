%module DSPlayer
%{
#include "..\DSPlayer.h"
%}



#define MAX_SIZE 256

class DSPlayer
{

public:
	DSPlayer();
	~DSPlayer();

	// does some initialization of the member variables
	HRESULT Initialize();

	// opens the file dialog and lets the user select a file
	virtual int OpenFileDialog();

	virtual int DoPlayOrPause();
	virtual int  DoStop();
	virtual int  DoPlay();
	//int  DoTimerStuff();
	//int  EventReceiver();
	virtual wchar_t* GetFileName();
	virtual bool GetIsPlaying(void);
};

DSPlayer*   CreateDSPlayerObject();

void  DeleteDSPlayerObject(DSPlayer*);

PyObject* GetFileName(DSPlayer& dp);


