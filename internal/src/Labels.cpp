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
    DEBUG("labels",cerr << "STARTING " << __FUNCTION__ << endl;);
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
    unsigned int cnt = 0;
    string current_label;
    DEBUG("labels",cerr << "STARTING " << __FUNCTION__ << endl;);
    do{ 
        current_label = labels_string[cnt];
        DEBUG("labels", cerr << "compare: " << current_label  << " with " << label << " gives " << current_label.compare(label) <<endl;);
        if(current_label.compare(label) == 0){
            // Label found
            DEBUG("labels",cerr << __FUNCTION__ << ": Label found("<<
                    cnt<< ")." << endl;);
            return cnt;
        }
        if(current_label.empty()){
            assert(cnt == current_size); 
            addLabel(label);
            DEBUG("labels",cerr << __FUNCTION__ << ": Label added("<<
                    cnt<< ")." << endl;);
            return cnt;
        }
        cnt++;
    }while(cnt < STRING_LABEL_ARRAY_SIZE);
    return -1;
}

int Labels::addLabel(string label){
    unsigned int lab_index = 0;
    DEBUG("labels",cerr << "STARTING " << __FUNCTION__ << endl;);
    if(current_size >= STRING_LABEL_ARRAY_SIZE)
        return -1; // too many labels

    assert(labels_string[current_size].empty());
    lab_index = current_size;
    labels_string[current_size] = label;
    current_size++;
    DEBUG("labels",cerr << "ENDING " << __FUNCTION__ << endl;);
    return lab_index;
}

/* PUBLIC FUNCTIONS */

int Labels::update(){
    // For each activated labels, increase counter.
    int cnt = 0;
    DEBUG("labels",cerr << "STARTING " << __FUNCTION__ << endl;);
    DEBUG("labels",cerr << __FUNCTION__ << 
            " current size: " << current_size << endl;);
    for(unsigned int i=0 ; i<current_size ; i++){
        if(labels_activated[i]){
            labels_counter[i]++;
            cnt++;
        }
        DEBUG("labels",cerr << __FUNCTION__ << ": activated["<<
                i << "] ? "<< labels_activated[i]<<
                " counter? "<<labels_counter[i] << endl;);
    }
    DEBUG("labels",cerr << "ENDING " << __FUNCTION__ << endl;);
    return cnt;
}

Value Labels::getJsonValue(){
    Value v;
    DEBUG("labels",cerr << "STARTING " << __FUNCTION__ << endl;);
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
    DEBUG("labels",cerr << "STARTING " << __FUNCTION__ << endl;);
    contain = containsLabel(label);
    DEBUG("labels",cerr << "Contain labels? ("<< contain << ")" << " current size? ("<<
            current_size<< ") "  << __FUNCTION__ << endl;);
    if(0 > contain){//=1? why?
        lab_index = addLabel(label);
    }else{
        lab_index = contain;
    }
    if(lab_index > -1)
        labels_activated[lab_index] = true;
    displayArrays();
    DEBUG("labels",cerr << "ENDING " << __FUNCTION__ << endl;);
    return lab_index;
}

int Labels::unSetInRegion(const char * label){
    string slabel(label);
    return unSetInRegion(slabel);
}

int Labels::unSetInRegion(string label){
    int contain = -1;
    int lab_index = -1;
    DEBUG("labels",cerr << "STARTING " << __FUNCTION__ << endl;);
    if(-1 == (contain = containsLabel(label)))
        return -2;//Should not unSet region which does not exist
    else
        lab_index = contain;
    labels_activated[lab_index] = false;
    return lab_index;
}
