#include <cassert>
#include <cstdlib>
#include <iostream>
#include <Labels.hpp>

#include "Debug.hpp"

using namespace std;

string Labels::labels_string[STRING_LABEL_ARRAY_SIZE];
bool   Labels::labels_activated[STRING_LABEL_ARRAY_SIZE];
unsigned int Labels::current_size;

Labels::Labels(){
    DEBUGINFO("STARTING");
    for(unsigned int i = 0 ; i < STRING_LABEL_ARRAY_SIZE ; i ++){
        labels_counter[i] = 0;
    }
}

void Labels::displayArrays(){
    cerr << " Current size " << current_size << endl;
    for(unsigned int i=0;i<current_size;i++){
        cerr << "String : " << labels_string[i]   << endl;
        cerr << "Counter : " << labels_counter[i]  << endl;
        cerr << "Activated: " << labels_activated[i]<< endl;
    }
}

/* Check if label exist. If not add it if possible.
 * Return -1 if impossible to add label.
 * otherwize return label index;
 * */
bool Labels::containsLabel(string label){
    DEBUGINFO("STARTING");
    unsigned int cnt = 0;
    string current_label;
    do{
        current_label = labels_string[cnt];
        DEBUGG("labels", "compare: " << current_label
                         << " with " << label << " gives "
                         << current_label.compare(label));
        if(current_label.compare(label) == 0){
            // Label found
            DEBUGG("labels","Label found(" << cnt << ").");
            return cnt;
        }
        if(current_label.empty()){
            assert(cnt == current_size);
            addLabel(label);
            DEBUGG("labels","Label added("<< cnt<< ").");
            return cnt;
        }
        cnt++;
    }while(cnt < STRING_LABEL_ARRAY_SIZE);
    return -1;
}

int Labels::addLabel(string label){
    unsigned int lab_index = 0;
    DEBUGINFO("STARTING ");
    if(current_size >= STRING_LABEL_ARRAY_SIZE)
        return -1; // too many labels

    assert(labels_string[current_size].empty());
    lab_index = current_size;
    labels_string[current_size] = label;
    current_size++;
    DEBUGINFO("ENDING");
    return lab_index;
}

/* PUBLIC FUNCTIONS */

int Labels::update(){
    // For each activated labels, increase counter.
    int cnt = 0;
    DEBUGG("labels", "current size: " << current_size);
    for(unsigned int i=0 ; i<current_size ; i++){
        if(labels_activated[i]){
            labels_counter[i]++;
            cnt++;
        }
        DEBUGG("labels","activated["<<
                i << "] ? "<< labels_activated[i]<<
                " counter? "<<labels_counter[i]);
    }
    DEBUGINFO("ENDING");
    return cnt;
}

Value Labels::getJsonValue(){
    Value v;
    for(unsigned int i=0 ; i<current_size ; i++){
        Value vint((UInt)labels_counter[i]);
        v[labels_string[i]] = vint;
    }
    return v;
}

int Labels::setInRegion(const char * label){
    string slabel(label);
    return setInRegion(slabel);
}
int Labels::setInRegion(string label){
    int contain = -1;
    int lab_index = -1;
    contain = containsLabel(label);
    DEBUGG("labels","Contain labels? ("<< contain
                    << ")" << " current size? ("
                    << current_size << ") ");
    if(0 > contain){
        lab_index = addLabel(label);
    }else{
        lab_index = contain;
    }
    if(lab_index > -1)
        labels_activated[lab_index] = true;
    //displayArrays(); TODO: DEBUG create operator <<
    DEBUGINFO("ENDING");
    return lab_index;
}

int Labels::unSetInRegion(const char * label){
    string slabel(label);
    return unSetInRegion(slabel);
}

int Labels::unSetInRegion(string label){
    DEBUGINFO("STARTING");
    int contain = -1;
    int lab_index = -1;
    if(-1 == (contain = containsLabel(label)))
        return -2;//Should not unSet region which does not exist
    else
        lab_index = contain;
    labels_activated[lab_index] = false;
    DEBUGINFO("ENDING");
    return lab_index;
}
